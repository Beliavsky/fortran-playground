"""Validate top-level GAMS assignments and generate their review page offline."""
import argparse
from collections import Counter
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPORT = Path('docs/fpm-gams.md')
GAMS_URL = 'https://gams.nist.gov/cgi-bin/serve.cgi'


def gams_data(root=ROOT):
    root = Path(root)
    data = json.loads((root / 'fpm_catalog/gams.json').read_text(encoding='utf-8'))
    if not isinstance(data, dict) or data.get('schema') != 1 or data.get('source') != GAMS_URL:
        raise ValueError('Invalid GAMS metadata schema or source.')
    classes = data.get('classes')
    if not isinstance(classes, dict) or set(classes) != set('ABCDEFGHIJKLMNOPQRSZ') or any(
            not isinstance(label, str) or not label.strip() for label in classes.values()):
        raise ValueError('GAMS metadata must define the 20 top-level classes.')
    packages = json.loads((root / 'fpm_catalog.json').read_text(encoding='utf-8'))['packages']
    expected = {p['id'] for p in packages}
    assignments = data.get('packages')
    if not isinstance(assignments, dict):
        raise ValueError('GAMS package assignments must be a mapping.')
    actual = set(assignments)
    if actual != expected:
        raise ValueError(f'GAMS assignments: missing {sorted(expected - actual)}, unknown {sorted(actual - expected)}.')
    for name, codes in assignments.items():
        if not isinstance(codes, list) or not codes or any(
                not isinstance(code, str) or code not in classes for code in codes):
            raise ValueError(f'{name}: use a nonempty list of top-level GAMS codes.')
        if len(codes) != len(set(codes)):
            raise ValueError(f'{name}: duplicate GAMS class.')
    return data


def package_classes(data, name):
    return [{'code': code, 'label': data['classes'][code]} for code in sorted(data['packages'][name])]


def review_text(root=ROOT):
    root = Path(root)
    data = gams_data(root)
    packages = json.loads((root / 'fpm_catalog.json').read_text(encoding='utf-8'))['packages']
    counts = Counter(code for codes in data['packages'].values() for code in codes)
    lines = ['# GAMS classifications for selected packages', '',
             f'All {len(packages)} selected packages have one or more top-level assignments from the '
             f'[NIST GAMS classification scheme]({GAMS_URL}). The assignments are maintained by the playground; '
             'they are not NIST or package-author endorsements.', '',
             'These broad discovery assignments are based on the saved package descriptions, categories, and topics. '
             'A class indicates relevant package functionality, not coverage of every problem in that class. '
             'Detailed routine classifications, verified problem drivers, and comparative benchmarks remain future work.', '',
             '## Searching', '',
             'Choose **GAMS class** in the hosted or main local FPM page. It combines with the text search, '
             'Category, topic-source choice, and sort order. Choose **All classes** to clear it. '
             'The explicit search syntax `GAMS D` (or `GAMS: D`) matches class D; ordinary searches also include '
             'the assigned class descriptions. GAMS classification is independent of the GitHub-only topic setting.', '',
             'Selected package details link to the NIST definitions. Other collections are not comprehensively '
             'classified: the translated R collection hides the filter, and the retained All collection includes '
             'assignments only for selected packages. Unclassified entries are excluded when a class is selected. '
             'Changing collections clears the class filter. Browsing and filtering do not submit jobs or contact NIST; '
             'opening a definition link visits NIST.', '',
             '## Classes', '', '| Code | NIST class | Selected packages |', '| --- | --- | --- |']
    for code, label in data['classes'].items():
        lines.append(f'| [{code}]({GAMS_URL}/Class/{code}) | {label} | {counts[code]} |')
    lines.extend(['', 'Counts overlap because a package may implement several kinds of problems. '
                  'All 20 classes remain in the filter, including classes with no current assignments.', '',
                  '## Classification choices', '',
                  '- Random-number generators use **L**, whose L6 subclass is random number generation. '
                  '[M](https://gams.nist.gov/cgi-bin/serve.cgi/Class/M) is reserved for simulation and stochastic modeling; '
                  'a stochastic optimization algorithm is classified under G rather than M just because it uses random numbers.',
                  '- Least-squares approximation and smoothing can appear under **K**, alongside **D**, **G**, or **L** '
                  'when the package also provides linear solvers, optimization, or statistical regression.',
                  '- Numeric expression parsers use **C/N**. Evaluating strings is not evidence of symbolic algebra under **O**.',
                  '- **P** includes geometric operations and graph algorithms; **N** includes graph storage and other data structures.',
                  '- **R** includes precision-support constants, error handling, and date/time services. '
                  'Domain-specific physical constants and thermodynamic properties use **Z**.', '',
                  '## Packages', '', '| Package at catalog revision | GAMS classes | Description |', '| --- | --- | --- |'])
    for package in sorted(packages, key=lambda p: p['id'].casefold()):
        classes = ', '.join(f'[{code} — {data["classes"][code]}]({GAMS_URL}/Class/{code})'
                            for code in sorted(data['packages'][package['id']]))
        description = package['description'].replace('|', '\\|').replace('\n', ' ')
        source = f'https://github.com/{package["repository"]}/tree/{package["revision"]}'
        lines.append(f'| [{package["id"]}]({source}) | {classes} | {description} |')
    lines.extend(['', '## Maintaining assignments', '',
                  'Edit [gams.json](../fpm_catalog/gams.json). Keep assignments separate from GitHub topics and '
                  'playground topics, and add an entry whenever a selected package is added. Use multiple classes '
                  'only for functionality the package provides.', '', '```text',
                  'python xpackage_gams.py', 'python xfpm_examples.py', '```', '',
                  'The first command validates complete catalog coverage and regenerates this page. '
                  'Use `python xpackage_gams.py --check` to check it without writing. The second regenerates '
                  'the public catalog assets. Both commands are offline; neither builds packages nor redeploys '
                  'the execution service. Class labels in the HTML filter are checked against this metadata by tests.', ''])
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Fail if the generated review page is out of date')
    args = parser.parse_args()
    text = review_text()
    path = ROOT / REPORT
    if args.check:
        if not path.exists() or path.read_text(encoding='utf-8') != text:
            parser.exit(1, 'GAMS review page is out of date. Run python xpackage_gams.py.\n')
        print('GAMS assignments and review page verified.')
    else:
        path.write_text(text, encoding='utf-8')
        print(f'Wrote {REPORT.as_posix()}')


if __name__ == '__main__':
    main()
