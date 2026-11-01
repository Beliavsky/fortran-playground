# Nonempty string / empty array probe

Pinned revision: `b9eb5e3fdc8f162ae8f2c5d8d026537ed2397830`. Source SHA256 (UTF-8 LF): `ec62cb80a92bf1bf0ff9529170cfd0f63cf4bff41a0e4c0053610b7ac537e152`.

Nonempty scalar strings precede empty rank-1/rank-2 arrays; the GNU 16 run segfaults at array extraction. Exact source/result retained.
