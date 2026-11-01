"""Independent integer oracle for the pinned rndgen-fortran KISS convention.

MIT: ../licenses/random-references-drivers-MIT.txt.
Uses unbounded Python integers, explicit modulo arithmetic and direct modular
Park--Miller multiplication, rather than Fortran signed overflow or Schrage's
decomposition. This checks the GNU build's wraparound convention, not Fortran
portability or statistical quality. No upstream implementation body is copied.
"""
import argparse
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
MASK = 2**32 - 1
MODULUS = 2**31 - 1
SEEDS = [0, 1, -1, 12345, -67890, 294727492, 2147483646]
COUNT = 4096


def stream(seed, count=COUNT):
    shuffled = (1099087573 * abs(seed)) % 2**32
    signed = shuffled if shuffled < 2**31 else shuffled - 2**32
    state = min(max(abs(signed), 1), MODULUS - 1)
    components = []
    for _ in range(4):
        state = (16807 * state) % MODULUS
        components.append(max(state, 1))
    x, y, z, w = components
    values = []
    # One discarded value is part of the pinned initialization convention.
    for index in range(count + 1):
        x = (69069 * x + 1327217885) % 2**32
        for shift in (13, -17, 5):
            shifted = (y * 2**shift) % 2**32 if shift > 0 else y // 2**(-shift)
            y = (y ^ shifted) & MASK
        z = 18000 * (z % 65536) + z // 65536
        w = 30903 * (w % 65536) + w // 65536
        value = ((x + y + z * 65536 + w) % 2**32) // 2
        if index:
            values.append(value)
    return values


def vectors():
    records = []
    for seed in SEEDS:
        values = stream(seed)
        checksum = 0
        for value in values:
            checksum = (65599 * checksum + value) % MODULUS
        records.append({'seed': seed, 'first_eight': values[:8], 'checksum': checksum})
    return {'schema': 1, 'package_revision': '3fa553608324913eed6cb178b398e7f661e4f63a',
            'samples_per_seed': COUNT, 'integer_scale': 2**31,
            'checksum_modulus': MODULUS, 'checksum_multiplier': 65599, 'vectors': records}


def constants(data):
    lines = ['   integer(int64), parameter :: prefix(8,streams)=reshape([ &']
    for index, record in enumerate(data['vectors']):
        values = [str(value)+'_int64' for value in record['first_eight']]
        lines.append('      '+', '.join(values[:4])+', &')
        suffix = ', &' if index + 1 < len(data['vectors']) else ' &'
        lines.append('      '+', '.join(values[4:])+suffix)
    lines += ['      ],[8,streams])', '   integer(int64), parameter :: expected_checksums(streams)=[ &']
    values = [str(record['checksum'])+'_int64' for record in data['vectors']]
    lines += ['      '+', '.join(values[:4])+', &', '      '+', '.join(values[4:])+']']
    return '\n'.join(lines)+'\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='Regenerate vectors and embedded consumer constants.')
    args = parser.parse_args()
    data = vectors()
    target = HERE/'kiss-vectors.json'
    driver = HERE.parent/'rndgen-kiss-reference.f90'
    before, rest = driver.read_text(encoding='utf-8').split('! BEGIN REFERENCE CONSTANTS\n')
    _, after = rest.split('! END REFERENCE CONSTANTS\n')
    source = before+'! BEGIN REFERENCE CONSTANTS\n'+constants(data)+'! END REFERENCE CONSTANTS\n'+after
    encoded = json.dumps(data, indent=2)+'\n'
    if args.write:
        target.write_text(encoded, encoding='utf-8')
        driver.write_text(source, encoding='utf-8')
    else:
        if target.read_text(encoding='utf-8') != encoded or driver.read_text(encoding='utf-8') != source:
            raise SystemExit('KISS reference vectors or consumer constants are stale.')
        print('Independent KISS integer vectors and consumer constants agree.')


if __name__ == '__main__':
    main()
