// Project downloads are assembled locally; no compilation service is contacted.
const encoder = new TextEncoder();

export function githubRepository(value) {
  try {
    const url = new URL(value);
    const parts = url.pathname.replace(/^\/+|\/+$/g, '').replace(/\.git$/, '').split('/');
    if (url.protocol !== 'https:' || url.host !== 'github.com' || url.search || url.hash
        || url.username || url.password || parts.length !== 2
        || parts.some(p => !/^[A-Za-z0-9_.-]+$/.test(p) || p === '.' || p === '..')) return '';
    return parts.join('/');
  } catch {return '';}
}

export function pinnedSource(packageEntry) {
  return packageEntry && githubRepository(`https://github.com/${packageEntry.repository}`)
    && /^[a-f0-9]{40}$/.test(packageEntry.revision)
    ? `https://github.com/${packageEntry.repository}/tree/${packageEntry.revision}`
      + (packageEntry.subdirectory ? '/' + encodeURIComponent(packageEntry.subdirectory) : '') : '';
}

export function projectFiles({source, stdin = '', url, revision, subdirectory = '', preprocess = false, packages, runtime}) {
  const repository = githubRepository(url);
  if (!repository || !/^[A-Za-z0-9_./-]{0,200}$/.test(revision)) throw new Error('Enter a valid GitHub repository and revision.');
  if (!source.trim()) throw new Error('Enter a main program before downloading a project.');
  if (subdirectory && (!/^[A-Za-z0-9_.-]+$/.test(subdirectory) || ['.', '..'].includes(subdirectory)
      || repository.toLowerCase() !== 'beliavsky/fortran-from-r-packages')) throw new Error('Invalid translated R package directory.');
  const packageEntry = packages.find(p => p.repository.toLowerCase() === repository.toLowerCase() && p.revision === revision
    && (p.subdirectory || '') === subdirectory && !subdirectory
    && /^[a-f0-9]{40}$/.test(p.revision) && /^[a-f0-9]{64}$/.test(p.archive_sha256));
  const {source: exampleSource, ...packageSettings} = packageEntry ?? {};
  const settings = {schema: 1, request: {url: `https://github.com/${repository}`, revision,
    ...(preprocess ? {preprocess: true} : {}),
    ...(subdirectory ? {subdirectory} : {})},
    ...(packageEntry ? {package: packageSettings} : {})};
  const system = packageSettings.catalog_build?.apt_packages ?? [];
  const requirements = system.length
    ? `\nNative libraries required by this recipe (recorded Debian package versions):\n${system.map(p => `- ${p}`).join('\n')}\nInstall equivalents on your system before building; these are not installed automatically.\n`
    : '\nInstall any external libraries required by the upstream package.\n';
  const files = {'app/main.f90': source,
    'fpm.toml': 'name = "playground-main"\n# Run python run.py to prepare the pinned package dependency first.\n',
    'playground.json': JSON.stringify(settings, null, 2) + '\n',
    'requirements.txt': 'tomli-w>=1,<3\n' + (Object.values(packageSettings.catalog_build?.source_packages || {}).some(s => s.fypp) ? 'fypp==3.2\n' : ''), ...runtime,
    'README.md': `# Downloaded FPM project\n\nYour edited main program is in app/main.f90.\n\n`
      + `Package source: https://github.com/${repository}/tree/${revision || 'HEAD'}${subdirectory ? '/' + encodeURIComponent(subdirectory) : ''}\n\n`
      + 'Requires Python 3.12+, FPM 0.12 or later, and a local GNU Fortran compiler (the catalog was tested with 16.2). Mixed-language packages also require GCC/G++.\n\n'
      + 'Extract the ZIP and run these commands from its directory:\n\n'
      + '```\npython -m pip install -r requirements.txt\npython run.py\n```\n\n'
      + 'Use `python run.py --build-only` to compile without running, or `python run.py --prepare-only` to download sources first. '
      + 'After preparation, fpm.toml refers to the local dependencies directory. The runner applies the catalog compiler/link flags; use it for subsequent builds too. '
      + 'Use `--compiler PATH` to select another local compiler executable; recipes with GNU-specific flags require adjustment before using other compiler families.\n'
      + requirements
      + '\nThe ZIP contains your main, configuration and preparation tools. Package source archives download on the first local run; this is not an offline source bundle. '
      + (packageEntry ? 'Catalog sources and dependencies are pinned and checksummed. Recorded manifest adaptations and patches are applied before compilation.\n'
        : 'This custom package uses the requested revision; its transitive dependencies are resolved when downloaded. Use a full commit for a fixed root revision.\n')
      + '\nSubsequent runs preserve prepared dependency files, including local edits. To change package settings or start over, extract a fresh project directory. '
      + 'Local builds do not reuse the hosted compiled libraries and may take several minutes. Local runs use your machine and contact no Modal service.\n'
      + (stdin ? '\nStandard input is saved as stdin.txt and supplied by the runner.\n' : '\nThe program can read standard input from your terminal.\n')
      + '\nIf your main uses pyplot_module, also install NumPy and Matplotlib: `python -m pip install numpy matplotlib`. '
      + 'The runner adds the plotting module when the package does not already supply it. Its license is in tools/pyplot-LICENSE.\n'
      + '\nDependency sources retain their upstream licensing. These preparation tools originate at https://github.com/Beliavsky/fortran-playground.\n'};
  if (stdin) files['stdin.txt'] = stdin;
  return files;
}

function crc32(bytes) {
  let crc = 0xffffffff;
  for (const byte of bytes) {
    crc ^= byte;
    for (let i = 0; i < 8; i++) crc = (crc >>> 1) ^ (0xedb88320 & -(crc & 1));
  }
  return (crc ^ 0xffffffff) >>> 0;
}

// Uncompressed ZIP records avoid a third-party ZIP runtime or a network service.
export function zipFiles(files) {
  const records = [], directory = [];
  let offset = 0, directorySize = 0;
  for (const [path, text] of Object.entries(files)) {
    if (path.startsWith('/') || path.split('/').some(p => !p || p === '..') || /[\\:\0]/.test(path)) throw new Error('Invalid ZIP path.');
    const name = encoder.encode(path), data = encoder.encode(text), crc = crc32(data);
    const local = new Uint8Array(30 + name.length), l = new DataView(local.buffer);
    l.setUint32(0, 0x04034b50, true); l.setUint16(4, 20, true); l.setUint16(6, 0x800, true);
    l.setUint16(12, 0x21, true); l.setUint32(14, crc, true);
    l.setUint32(18, data.length, true); l.setUint32(22, data.length, true); l.setUint16(26, name.length, true);
    local.set(name, 30);
    const central = new Uint8Array(46 + name.length), c = new DataView(central.buffer);
    c.setUint32(0, 0x02014b50, true); c.setUint16(4, 20, true); c.setUint16(6, 20, true);
    c.setUint16(8, 0x800, true); c.setUint16(14, 0x21, true); c.setUint32(16, crc, true);
    c.setUint32(20, data.length, true); c.setUint32(24, data.length, true); c.setUint16(28, name.length, true);
    c.setUint32(42, offset, true); central.set(name, 46);
    records.push(local, data); directory.push(central); directorySize += central.length;
    offset += local.length + data.length;
  }
  const end = new Uint8Array(22), e = new DataView(end.buffer);
  e.setUint32(0, 0x06054b50, true); e.setUint16(8, directory.length, true); e.setUint16(10, directory.length, true);
  e.setUint32(12, directorySize, true); e.setUint32(16, offset, true);
  return new Blob([...records, ...directory, end], {type: 'application/zip'});
}

export function download(blob, filename) {
  const link = document.createElement('a'), url = URL.createObjectURL(blob);
  link.href = url; link.download = filename; link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
