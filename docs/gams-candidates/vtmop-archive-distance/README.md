# Retained vtmop-archive-distance probe

The initial four-search consumer required every returned archive point to lie within relative distance 0.15 of the exact Pareto segment. Both 2-D runs passed with maximum 0.128205, but the first 3-D run failed that assertion. Exact failing main and full service result are retained. The revised consumer requires a nontrivial near-front subset and report all-point distances without claiming the entire finite archive is uniformly close. No tolerance or solver change fixes the retained failed assertion.

Pinned revision: `794a1de23801731ef6edd1924b52d69b679af6a0`. Source SHA256 (UTF-8 LF): `0b51689357b34f0cb0b1fa77bd8a9c0ba672abf68e87027cdb6ab2fdf2890f3c`.

[Exact main](driver.f90) | [Full cached GNU 16 result](result.json).
