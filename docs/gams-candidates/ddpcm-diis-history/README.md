# Retained ddpcm-diis-history probe

The initial manufactured-system consumer used DIIS history 4. The pinned diis routine unconditionally removes ten entries when nmat reaches ndiis, making nmat negative. GNU 16 bounds checking stops at makeb with array index -5. The published consumer uses the package default history 25; no library patch is applied. This is a history-size implementation limitation, not a failure of plain Jacobi.

Pinned revision: `36f22feb86c81c6ba1f59c373ef215368d3e3c13`. Source SHA256 (UTF-8 LF): `a9db9ff41c6f3f9ef3ac5d9aefee749008f382858a11459385eb0f24fabd76c3`.

[Exact main](driver.f90) | [Full cached GNU 16 result](result.json).
