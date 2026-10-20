"""Generate a standalone HTML index of links that load Fortran into the playground."""
import argparse
from html import escape
from pathlib import Path
import re
import sys
from urllib.parse import quote, urlsplit, urlunsplit

DEFAULT_PLAYGROUND = 'https://beliavsky.github.io/fortran-playground/'
EXTENSIONS = {'.f90', '.f95', '.f03', '.f08'}
MAX_SOURCE_BYTES = 100000


def build_link_page(directory: Path, output: Path, *, recursive=False,
                    title='Fortran examples', playground_url=DEFAULT_PLAYGROUND):
    """Write the page; return the link count and warnings for skipped/long files."""
    if not directory.is_dir():
        raise ValueError(f'Not a directory: {directory}')
    url = urlsplit(playground_url)
    if url.scheme not in {'http', 'https'} or not url.netloc or url.username or url.password:
        raise ValueError('The playground URL must be an HTTP(S) URL without credentials.')
    base = urlunsplit((url.scheme, url.netloc, url.path, '', ''))
    paths = sorted((p for p in (directory.rglob('*') if recursive else directory.glob('*'))
                    if p.is_file() and p.suffix.lower() in EXTENSIONS),
                   key=lambda p: p.relative_to(directory).as_posix())
    if any(p.resolve() == output.resolve() for p in paths):
        raise ValueError('The output would overwrite a Fortran source file.')
    rows, warnings = [], []
    for path in paths:
        name = path.relative_to(directory).as_posix()
        try:
            if path.stat().st_size > MAX_SOURCE_BYTES + 3:
                raise ValueError('exceeds the 100 KB source limit')
            # Decode bytes directly to preserve CRLF line endings. Strip a UTF-8 BOM.
            source = path.read_bytes().decode('utf-8-sig')
            if not source.strip():
                raise ValueError('source is empty')
            if len(source.encode('utf-8')) > MAX_SOURCE_BYTES:
                raise ValueError('exceeds the 100 KB source limit')
        except (OSError, UnicodeError, ValueError) as error:
            warnings.append(f'Skipped {name}: {error}')
            continue
        heading = re.search(r'^\s*!\s*Example:\s*(\S[^\r\n]*)', source, re.MULTILINE)
        label = heading.group(1).strip() if heading else path.stem
        link = base + '#code=' + quote(source, safe='')
        if len(link) > 8000:
            warnings.append(f'{name}: long link ({len(link)} characters) may be truncated by some sites')
        rows.append(f'<li><a href="{escape(link, quote=True)}">{escape(label)}</a>'
                    f' <small>{escape(name)}</small></li>')
    listing = '<ul>\n' + '\n'.join(rows) + '\n</ul>' if rows else '<p>No eligible Fortran examples found.</p>'
    html = f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)}</title>
  <style>
    body {{ font-family: system-ui, sans-serif; max-width: 60rem; margin: 3rem auto; padding: 0 1rem; line-height: 1.6; }}
    li {{ margin: 0.6rem 0; overflow-wrap: anywhere; }}
    small {{ display: block; color: #555; }}
  </style>
</head>
<body>
<h1>{escape(title)}</h1>
<p>{len(rows)} examples. Choose a link to open its code in the Fortran playground.
Compilation and execution require a button click there.</p>
{listing}
<p>These links contain source snapshots. Regenerate this page after changing the files.
Long links may be truncated when shared through other sites.</p>
</body>
</html>
'''
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html, encoding='utf-8')
    return len(rows), warnings


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path, help='Directory of UTF-8 Fortran source files')
    parser.add_argument('-o', '--output', type=Path, default=Path('playground-links.html'), help='Output HTML file')
    parser.add_argument('-r', '--recursive', action='store_true', help='Include subdirectories')
    parser.add_argument('--title', default='Fortran examples', help='Page title')
    parser.add_argument('--playground-url', default=DEFAULT_PLAYGROUND, help='Playground entry-point URL')
    args = parser.parse_args(argv)
    try:
        count, warnings = build_link_page(args.directory, args.output, recursive=args.recursive,
                                         title=args.title, playground_url=args.playground_url)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    for warning in warnings:
        print(f'Warning: {warning}', file=sys.stderr)
    print(f'Wrote {count} playground links to {args.output}')


if __name__ == '__main__':
    main()
