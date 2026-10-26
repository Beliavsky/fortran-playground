"""Optional comparisons of captured stdout; never executes code or changes streams."""
import re

MODES = ('whitespace', 'exact', 'numeric')
LIMIT = 1_000_000
TOKEN = re.compile(r'''('(?:[^']|'')*'|"(?:[^"]|"")*"|\*{2,}|\.(?:true|false)\.|[^\W\d]\w*(?:\.\w+)*|[+-]?(?:infinity|inf|nan)\b|[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eEdD][+-]?[0-9]+)?|[^\s])''', re.I)
NUMBER = re.compile(r'^[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eEdD][+-]?[0-9]+)?$')
SPECIAL = re.compile(r'^[+-]?(?:infinity|inf|nan)$|^\*{2,}$', re.I)


def decimal(value):
    text = str(value)
    if len(text) > 2200 or not NUMBER.fullmatch(text):
        raise ValueError('Use finite nonnegative decimal tolerances; numeric tokens must have bounded length.')
    parts = re.split('[eEdD]', text)
    exponent = int(parts[1]) if len(parts) == 2 else 0
    if abs(exponent) > 2000:
        raise ValueError('Numeric exponent exceeds comparison limit (2000).')
    mantissa = parts[0]
    exponent -= len(mantissa.split('.')[1]) if '.' in mantissa else 0
    digits = mantissa.replace('.', '')
    if len(digits.lstrip('+-')) > 2000:
        raise ValueError('Numeric token exceeds comparison limit (2000 digits).')
    return int(digits), exponent


def aligned(a, b):
    exponent = min(a[1], b[1])
    return a[0] * 10 ** (a[1] - exponent), b[0] * 10 ** (b[1] - exponent), exponent


def compare_decimal(a, b):
    x, y, _ = aligned(a, b)
    return (x > y) - (x < y)


def tolerances(atol='0', rtol='0'):
    values = decimal(atol), decimal(rtol)
    if any(value[0] < 0 for value in values):
        raise ValueError('Tolerances must be finite and nonnegative.')
    return values


def close(a, b, absolute, relative):
    x, y, exponent = aligned(a, b)
    difference = abs(x - y), exponent
    aa, bb = (abs(a[0]), a[1]), (abs(b[0]), b[1])
    scale = aa if compare_decimal(aa, bb) >= 0 else bb
    bound = relative[0] * scale[0], relative[1] + scale[1]
    bound = absolute if compare_decimal(absolute, bound) >= 0 else bound
    return compare_decimal(difference, bound) <= 0


def compare_output(left, right, mode='whitespace', atol='0', rtol='0'):
    absolute, relative = tolerances(atol, rtol)
    if mode not in MODES:
        raise ValueError('Unknown output comparison mode')
    if len(left) > LIMIT or len(right) > LIMIT:
        return {'status': 'Not comparable', 'detail': 'Output exceeds the 1,000,000-character comparison limit.'}
    a, b = [text.replace('\r\n', '\n').replace('\r', '\n') for text in (left, right)]
    detail = ''
    if mode == 'numeric':
        ta, tb = TOKEN.findall(a), TOKEN.findall(b)
        if max(len(ta), len(tb)) > 20000:
            return {'status': 'Not comparable', 'detail': 'More than 20,000 output tokens.'}
        if any(SPECIAL.fullmatch(token) for token in ta + tb):
            return {'status': 'Not comparable', 'detail': 'NaN, infinity, or overflow fields present; inspect raw output.'}
        if len(ta) != len(tb):
            detail = f'Token counts differ: reference {len(ta)}, output {len(tb)}.'
        tolerant = False
        try:
            for index, (x, y) in enumerate(zip(ta, tb), 1):
                if detail:
                    break
                if x == y:
                    continue
                if x.lower() in ('t', '.true.', 'f', '.false.') and y.lower() in ('t', '.true.', 'f', '.false.'):
                    same = (x.lower() in ('t', '.true.')) == (y.lower() in ('t', '.true.'))
                elif NUMBER.fullmatch(x) and NUMBER.fullmatch(y):
                    dx, dy = decimal(x), decimal(y)
                    equal = compare_decimal(dx, dy) == 0
                    integers = re.fullmatch(r'[+-]?\d+', x) and re.fullmatch(r'[+-]?\d+', y)
                    same = equal or (not integers and close(dx, dy, absolute, relative))
                    tolerant |= same and not equal
                else:
                    same = False
                if not same:
                    detail = f'Token {index}: reference {x[:160]!r}, output {y[:160]!r}.'
        except ValueError as error:
            return {'status': 'Not comparable', 'detail': str(error)}
        if not detail:
            status = 'Exact match' if a == b else 'Formatting only' if ' '.join(a.split()) == ' '.join(b.split()) else 'Within tolerance' if tolerant else 'Numeric match'
            return {'status': status, 'detail': ''}
    elif a == b:
        return {'status': 'Exact match', 'detail': ''}
    elif mode == 'whitespace' and ' '.join(a.split()) == ' '.join(b.split()):
        return {'status': 'Formatting only', 'detail': ''}
    if not detail:
        aa, bb = (a.split() if mode == 'whitespace' else a.split('\n')), (b.split() if mode == 'whitespace' else b.split('\n'))
        index = next((i for i in range(max(len(aa), len(bb))) if (aa[i] if i < len(aa) else None) != (bb[i] if i < len(bb) else None)), 0)
        detail = f'{"Token" if mode == "whitespace" else "Line"} {index + 1}: reference {str(aa[index] if index < len(aa) else "<end>")[:160]!r}, output {str(bb[index] if index < len(bb) else "<end>")[:160]!r}.'
    return {'status': 'Different', 'detail': detail}


def comparable(row):
    result = row.get('result', row)
    execution = result.get('execution')
    if row.get('status', 'PASS') != 'PASS' or result.get('ok') is False or not execution:
        return False
    if execution.get('ok') is False or execution.get('exit_code') not in (None, 0) or execution.get('timed_out') or execution.get('cancelled'):
        return False
    return not (execution.get('truncated') or execution.get('stdout_truncated') or
                re.search(r'Output was truncated at the configured per-stream limit\.|Output limit exceeded\.', execution.get('stderr') or '', re.I))


def comparison_report(rows, mode='whitespace', atol='0', rtol='0', reference=''):
    tolerances(atol, rtol)
    baseline = next((row for row in rows if comparable(row) and (not reference or row['compiler'] == reference)), None)
    lines = [f'Output comparison: {mode}; stdout only; atol={atol}, rtol={rtol}',
             f'Reference: {baseline["compiler"] if baseline else "unavailable (no successful complete run)"}']
    for row in rows:
        if not baseline or not comparable(row):
            outcome = {'status': 'Not comparable', 'detail': 'Requires a successful, complete execution and reference.'}
        elif row is baseline:
            text = baseline.get('result', baseline)['execution'].get('stdout') or ''
            outcome = compare_output(text, text, mode, atol, rtol)
            if outcome['status'] != 'Not comparable':
                outcome = {'status': 'Reference', 'detail': ''}
        else:
            outcome = compare_output(baseline.get('result', baseline)['execution'].get('stdout') or '', row.get('result', row)['execution'].get('stdout') or '', mode, atol, rtol)
        lines.append(f'{row["compiler"]}: {outcome["status"]}' + (f' — {outcome["detail"]}' if outcome['detail'] else ''))
    return '\n'.join(lines)


def add_diff_arguments(parser):
    parser.add_argument('--diff', nargs='?', const='whitespace', choices=MODES, help='Compare captured stdout (default mode: whitespace); off unless requested')
    parser.add_argument('--diff-atol', default='0', help='Absolute tolerance for numeric output comparison (default: 0)')
    parser.add_argument('--diff-rtol', default='0', help='Relative tolerance for numeric output comparison (default: 0)')
    parser.add_argument('--diff-reference', default='', help='Reference compiler; default: first successful complete execution')


def validate_diff_arguments(args, names):
    tolerances(args.diff_atol, args.diff_rtol)
    if args.diff_reference and args.diff_reference not in names:
        raise ValueError('--diff-reference must name a selected compiler')
    if not args.diff and (args.diff_atol != '0' or args.diff_rtol != '0' or args.diff_reference):
        raise ValueError('Use --diff to enable output comparison')
    if args.diff != 'numeric' and (args.diff_atol != '0' or args.diff_rtol != '0'):
        raise ValueError('Tolerances require --diff numeric')
