// Query settings configure the page; they never request execution.
const compilers = ['gfortran', 'gfortran17', 'ifx', 'flang', 'lfortran', 'ofort'];
const standards = ['default', '1995', '2003', '2008', '2018', '2023'];

export function parseURLSettings(search) {
  const parameters = new URLSearchParams(search), settings = {}, warnings = [];
  for (const key of ['interface', 'compiler', 'compilers', 'example', 'standard', 'preprocess']) {
    if (!parameters.has(key)) continue;
    if (parameters.getAll(key).length !== 1) {warnings.push(`Duplicate URL setting: ${key}.`); continue;}
    const value = parameters.get(key);
    let valid = false;
    if (key === 'interface') valid = ['simple', 'advanced', 'compare'].includes(value);
    if (key === 'compiler') valid = compilers.includes(value);
    if (key === 'compilers') valid = value.split(',').length <= compilers.length && value.split(',').every(name => compilers.includes(name)) && new Set(value.split(',')).size === value.split(',').length;
    if (key === 'example') valid = /^[A-Za-z0-9_-]{1,128}$/.test(value);
    if (key === 'standard') valid = standards.includes(value);
    if (key === 'preprocess') valid = ['0', '1'].includes(value);
    if (!valid) {warnings.push(`Invalid URL setting: ${key}.`); continue;}
    settings[key] = key === 'compilers' ? value.split(',') : key === 'preprocess' ? value === '1' : value;
  }
  if (!settings.interface) {
    if (settings.compilers) settings.interface = 'compare';
    else if (['compiler', 'standard', 'preprocess'].some(key => Object.hasOwn(settings, key))) settings.interface = 'advanced';
  }
  if (settings.interface === 'simple') {
    for (const key of ['compiler', 'compilers', 'standard', 'preprocess']) {
      if (!Object.hasOwn(settings, key)) continue;
      warnings.push(`URL setting ${key} is ignored in the Simple interface.`); delete settings[key];
    }
  }
  if (settings.compilers && settings.interface !== 'compare') {
    warnings.push('URL setting compilers requires the Compare compilers interface.'); delete settings.compilers;
  }
  return {settings, warnings};
}
