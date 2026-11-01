"""Unsigned Python oracle for pinned xoroshiro128+(24,16,37) API vectors.

MIT: ../licenses/helmholtz-streams-drivers-MIT.txt. No package imports.
The jump oracle squares a 128-column GF(2) transition matrix 64 times;
it neither uses nor copies the upstream jump-polynomial constants.
"""
import json
from pathlib import Path

MASK = (1 << 64) - 1
PRIME = (1 << 31) - 1
SEEDS = [(1, 2), (MASK, 1), (1 << 63, (1 << 63)-1),
         (123456789, 987654321), (0x0123456789ABCDEF, 0xFEDCBA9876543210)]


def transition(state):
    a, b = state & MASK, state >> 64
    b ^= a
    a = (((a << 24) | (a >> 40)) ^ b ^ (b << 16)) & MASK
    b = ((b << 37) | (b >> 27)) & MASK
    return a | (b << 64)


def apply(columns, state):
    result = 0
    while state:
        lowest = state & -state
        result ^= columns[lowest.bit_length()-1]
        state ^= lowest
    return result


def jump_columns():
    columns = [transition(1 << bit) for bit in range(128)]
    for _ in range(64):
        columns = [apply(columns, column) for column in columns]
    return columns


def vectors():
    columns = jump_columns()
    streams = []
    for seed in SEEDS:
        for jumps in range(3):
            state = seed[0] | (seed[1] << 64)
            for _ in range(jumps):
                state = apply(columns, state)
            prefix, integer_hash, uniform_hash = [], 0, 0
            for sample in range(4096):
                value = ((state & MASK) + (state >> 64)) & MASK
                state = transition(state)
                if sample < 8:
                    prefix.append(f'{value:016X}')
                integer_hash = (65599*integer_hash + value) % PRIME
                uniform_hash = (65599*uniform_hash + (value >> 12)) % PRIME
            streams.append({'seed_hex': [f'{x:016X}' for x in seed], 'jumps': jumps,
                            'prefix_hex': prefix, 'integer_hash': integer_hash,
                            'uniform_hash': uniform_hash})
    return {'schema': 1, 'algorithm': 'xoroshiro128+(24,16,37)',
            'jump_reference': 'GF(2) transition matrix raised to 2**64',
            'samples_per_stream': 4096, 'streams': streams}


if __name__ == '__main__':
    destination = Path(__file__).with_name('xoroshiro-vectors.json')
    destination.write_text(json.dumps(vectors(), indent=2)+'\n', encoding='utf-8')
