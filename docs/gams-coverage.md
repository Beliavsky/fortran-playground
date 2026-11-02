# GAMS classification and checked-driver coverage

**The GAMS categories are not exhausted.** Some procedures already map to the deepest available GAMS class, but that does not mean all procedures or problem configurations in that class have been demonstrated.

The selected catalog has 510 source-reviewed procedure records. 483 independently checked drivers cover 483 of those records and 19 of the 20 top-level GAMS classes. Among the 157 maintained classes used directly by procedure records, 1 still has no class-specific checked driver.

These counts concern the dedicated GAMS drivers. The ordinary precompiled-package demonstrations have their own build/run verification and are not counted as class-specific drivers here.

## What these counts mean

- Package assignments are discovery classifications and may describe capabilities beyond the reviewed procedures.
- A source-reviewed procedure has pinned API/source evidence. This alone does not mean a matching driver has been run.
- A checked driver demonstrates its recorded procedure and problem class with saved successful sandbox evidence. It does not cover every overload or input.
- Reaching a taxonomy leaf, such as F1b or E1a, means there is no finer GAMS category in the recorded taxonomy. Additional procedures, drivers and non-GAMS descriptors can still distinguish useful capabilities.

This is coverage of our maintained selected-package records, **not a complete inventory of the GAMS taxonomy or all Fortran software**. A class with a checked driver is not marked exhausted. Empty categories may lack a suitable selected package; other categories have many source-reviewed procedures awaiting drivers.

## Top-level coverage

Procedure and driver counts include descendants. A procedure assigned to multiple categories may appear in multiple rows, so the rows should not be summed.

| Class | Description | Assigned packages | Reviewed procedures | Procedures with checked drivers | Drivers |
| --- | --- | ---: | ---: | ---: | ---: |
| [A](https://beliavsky.github.io/fortran-playground/gams/A/) | Arithmetic, error analysis | 13 | 12 | 10 | 10 |
| [B](https://beliavsky.github.io/fortran-playground/gams/B/) | Number theory | 3 | 3 | 3 | 3 |
| [C](https://beliavsky.github.io/fortran-playground/gams/C/) | Elementary and special functions | 12 | 55 | 51 | 51 |
| [D](https://beliavsky.github.io/fortran-playground/gams/D/) | Linear Algebra | 39 | 140 | 136 | 136 |
| [E](https://beliavsky.github.io/fortran-playground/gams/E/) | Interpolation | 13 | 19 | 17 | 17 |
| [F](https://beliavsky.github.io/fortran-playground/gams/F/) | Solution of nonlinear equations | 8 | 18 | 17 | 17 |
| [G](https://beliavsky.github.io/fortran-playground/gams/G/) | Optimization | 22 | 25 | 25 | 25 |
| [H](https://beliavsky.github.io/fortran-playground/gams/H/) | Differentiation, integration | 24 | 38 | 34 | 34 |
| [I](https://beliavsky.github.io/fortran-playground/gams/I/) | Differential and integral equations | 27 | 31 | 26 | 26 |
| [J](https://beliavsky.github.io/fortran-playground/gams/J/) | Integral transforms | 11 | 15 | 15 | 15 |
| [K](https://beliavsky.github.io/fortran-playground/gams/K/) | Approximation | 19 | 7 | 6 | 6 |
| [L](https://beliavsky.github.io/fortran-playground/gams/L/) | Statistics, probability | 19 | 55 | 49 | 49 |
| [M](https://beliavsky.github.io/fortran-playground/gams/M/) | Simulation, stochastic modeling | 2 | 1 | 1 | 1 |
| [N](https://beliavsky.github.io/fortran-playground/gams/N/) | Data handling | 101 | 62 | 59 | 59 |
| [O](https://beliavsky.github.io/fortran-playground/gams/O/) | Symbolic computation | 0 | 0 | 0 | 0 |
| [P](https://beliavsky.github.io/fortran-playground/gams/P/) | Computational geometry | 14 | 11 | 8 | 8 |
| [Q](https://beliavsky.github.io/fortran-playground/gams/Q/) | Graphics | 12 | 6 | 1 | 1 |
| [R](https://beliavsky.github.io/fortran-playground/gams/R/) | Service routines | 19 | 17 | 14 | 14 |
| [S](https://beliavsky.github.io/fortran-playground/gams/S/) | Software development tools | 17 | 10 | 10 | 10 |
| [Z](https://beliavsky.github.io/fortran-playground/gams/Z/) | Other | 11 | 1 | 1 | 1 |

## Direct procedure-class coverage

These are the most specific classes currently recorded for procedures, not necessarily leaves of the full GAMS taxonomy. Counts are exact class matches. For example, an analytic-gradient driver does not check a derivative-free configuration of the same generic procedure.

| Class | Label (read with ancestors) | Reviewed procedures | Procedures with checked drivers | Drivers |
| --- | --- | ---: | ---: | ---: |
| [A](https://beliavsky.github.io/fortran-playground/gams/A/) | Arithmetic, error analysis | 1 | 1 | 1 |
| [A1](https://beliavsky.github.io/fortran-playground/gams/A1/) | Integer | 4 | 2 | 2 |
| [A2](https://beliavsky.github.io/fortran-playground/gams/A2/) | Rational | 1 | 1 | 1 |
| [A3a](https://beliavsky.github.io/fortran-playground/gams/A3a/) | Standard precision | 1 | 1 | 1 |
| [A3c](https://beliavsky.github.io/fortran-playground/gams/A3c/) | Extended precision | 1 | 1 | 1 |
| [A4](https://beliavsky.github.io/fortran-playground/gams/A4/) | Complex | 1 | 1 | 1 |
| [A4c](https://beliavsky.github.io/fortran-playground/gams/A4c/) | Extended precision | 1 | 1 | 1 |
| [A6](https://beliavsky.github.io/fortran-playground/gams/A6/) | Change of representation | 3 | 2 | 2 |
| [B](https://beliavsky.github.io/fortran-playground/gams/B/) | Number theory | 3 | 3 | 3 |
| [C1](https://beliavsky.github.io/fortran-playground/gams/C1/) | Integer-valued functions (e.g., factorial, binomial coefficient, permutations, combinations, floor, ceiling) | 1 | 1 | 1 |
| [C2](https://beliavsky.github.io/fortran-playground/gams/C2/) | Powers, roots, reciprocals | 3 | 2 | 2 |
| [C3a2](https://beliavsky.github.io/fortran-playground/gams/C3a2/) | Chebyshev, Legendre | 1 | 1 | 1 |
| [C4](https://beliavsky.github.io/fortran-playground/gams/C4/) | Elementary transcendental functions | 1 | 1 | 1 |
| [C4a](https://beliavsky.github.io/fortran-playground/gams/C4a/) | Trigonometric, inverse trigonometric | 1 | 1 | 1 |
| [C4b](https://beliavsky.github.io/fortran-playground/gams/C4b/) | Exponential, logarithmic | 2 | 2 | 2 |
| [C4d](https://beliavsky.github.io/fortran-playground/gams/C4d/) | Integrals of elementary transcendental functions | 2 | 1 | 1 |
| [C5](https://beliavsky.github.io/fortran-playground/gams/C5/) | Exponential and logarithmic integrals | 3 | 3 | 3 |
| [C6](https://beliavsky.github.io/fortran-playground/gams/C6/) | Cosine and sine integrals | 2 | 2 | 2 |
| [C7](https://beliavsky.github.io/fortran-playground/gams/C7/) | Gamma | 1 | 1 | 1 |
| [C7a](https://beliavsky.github.io/fortran-playground/gams/C7a/) | Gamma, log gamma, reciprocal gamma | 8 | 8 | 8 |
| [C7b](https://beliavsky.github.io/fortran-playground/gams/C7b/) | Beta, log beta | 3 | 3 | 3 |
| [C7c](https://beliavsky.github.io/fortran-playground/gams/C7c/) | Psi function | 1 | 1 | 1 |
| [C7e](https://beliavsky.github.io/fortran-playground/gams/C7e/) | Incomplete gamma | 7 | 6 | 6 |
| [C7f](https://beliavsky.github.io/fortran-playground/gams/C7f/) | Incomplete beta | 1 | 1 | 1 |
| [C8c](https://beliavsky.github.io/fortran-playground/gams/C8c/) | Dawson's integral | 1 | 1 | 1 |
| [C10](https://beliavsky.github.io/fortran-playground/gams/C10/) | Bessel functions | 2 | 1 | 1 |
| [C10b1](https://beliavsky.github.io/fortran-playground/gams/C10b1/) | Real argument, integer order | 3 | 3 | 3 |
| [C10d](https://beliavsky.github.io/fortran-playground/gams/C10d/) | Airy and Scorer functions | 1 | 1 | 1 |
| [C14](https://beliavsky.github.io/fortran-playground/gams/C14/) | Elliptic integrals | 1 | 1 | 1 |
| [C19](https://beliavsky.github.io/fortran-playground/gams/C19/) | Other special functions | 12 | 10 | 10 |
| [D](https://beliavsky.github.io/fortran-playground/gams/D/) | Linear Algebra | 3 | 3 | 3 |
| [D1](https://beliavsky.github.io/fortran-playground/gams/D1/) | Elementary vector and matrix operations | 6 | 6 | 6 |
| [D1a3](https://beliavsky.github.io/fortran-playground/gams/D1a3/) | Norm | 1 | 1 | 1 |
| [D1a5](https://beliavsky.github.io/fortran-playground/gams/D1a5/) | Copy or exchange (swap) | 1 | 1 | 1 |
| [D1a11](https://beliavsky.github.io/fortran-playground/gams/D1a11/) | Other vector operations | 6 | 6 | 6 |
| [D1b](https://beliavsky.github.io/fortran-playground/gams/D1b/) | Elementary matrix operations | 2 | 2 | 2 |
| [D1b1](https://beliavsky.github.io/fortran-playground/gams/D1b1/) | Initialize (e.g., to zero or identity) | 3 | 3 | 3 |
| [D1b2](https://beliavsky.github.io/fortran-playground/gams/D1b2/) | Norm | 2 | 2 | 2 |
| [D1b3](https://beliavsky.github.io/fortran-playground/gams/D1b3/) | Transpose | 1 | 1 | 1 |
| [D1b4](https://beliavsky.github.io/fortran-playground/gams/D1b4/) | Multiplication by vector | 2 | 2 | 2 |
| [D1b6](https://beliavsky.github.io/fortran-playground/gams/D1b6/) | Multiplication | 4 | 4 | 4 |
| [D1b9](https://beliavsky.github.io/fortran-playground/gams/D1b9/) | Storage mode conversion | 1 | 1 | 1 |
| [D2](https://beliavsky.github.io/fortran-playground/gams/D2/) | Solution of systems of linear equations (including inversion, LU and related decompositions) | 6 | 6 | 6 |
| [D2a1](https://beliavsky.github.io/fortran-playground/gams/D2a1/) | General | 11 | 11 | 11 |
| [D2a2a](https://beliavsky.github.io/fortran-playground/gams/D2a2a/) | Tridiagonal | 1 | 1 | 1 |
| [D2a3](https://beliavsky.github.io/fortran-playground/gams/D2a3/) | Triangular | 2 | 2 | 2 |
| [D2a4](https://beliavsky.github.io/fortran-playground/gams/D2a4/) | Sparse | 2 | 2 | 2 |
| [D2b1a](https://beliavsky.github.io/fortran-playground/gams/D2b1a/) | Indefinite | 1 | 1 | 1 |
| [D2b1b](https://beliavsky.github.io/fortran-playground/gams/D2b1b/) | Positive definite | 9 | 9 | 9 |
| [D2b2a](https://beliavsky.github.io/fortran-playground/gams/D2b2a/) | Tridiagonal | 2 | 2 | 2 |
| [D2b4](https://beliavsky.github.io/fortran-playground/gams/D2b4/) | Sparse | 2 | 2 | 2 |
| [D2c1](https://beliavsky.github.io/fortran-playground/gams/D2c1/) | General | 2 | 2 | 2 |
| [D2d1b](https://beliavsky.github.io/fortran-playground/gams/D2d1b/) | Positive definite | 3 | 3 | 3 |
| [D3a1](https://beliavsky.github.io/fortran-playground/gams/D3a1/) | General | 1 | 1 | 1 |
| [D3a2a](https://beliavsky.github.io/fortran-playground/gams/D3a2a/) | Tridiagonal | 1 | 1 | 1 |
| [D3b2a](https://beliavsky.github.io/fortran-playground/gams/D3b2a/) | Tridiagonal | 1 | 1 | 1 |
| [D3c1](https://beliavsky.github.io/fortran-playground/gams/D3c1/) | General | 1 | 1 | 1 |
| [D4](https://beliavsky.github.io/fortran-playground/gams/D4/) | Eigenvalues, eigenvectors | 1 | 1 | 1 |
| [D4a1](https://beliavsky.github.io/fortran-playground/gams/D4a1/) | Real symmetric | 11 | 10 | 10 |
| [D4a2](https://beliavsky.github.io/fortran-playground/gams/D4a2/) | Real nonsymmetric | 4 | 4 | 4 |
| [D4a3](https://beliavsky.github.io/fortran-playground/gams/D4a3/) | Complex Hermitian | 1 | 1 | 1 |
| [D4a4](https://beliavsky.github.io/fortran-playground/gams/D4a4/) | Complex non-Hermitian | 2 | 2 | 2 |
| [D4a5](https://beliavsky.github.io/fortran-playground/gams/D4a5/) | Tridiagonal | 1 | 1 | 1 |
| [D4b2](https://beliavsky.github.io/fortran-playground/gams/D4b2/) | Real general | 1 | 1 | 1 |
| [D4b4](https://beliavsky.github.io/fortran-playground/gams/D4b4/) | Complex general | 1 | 1 | 1 |
| [D4c](https://beliavsky.github.io/fortran-playground/gams/D4c/) | Associated operations | 1 | 1 | 1 |
| [D5](https://beliavsky.github.io/fortran-playground/gams/D5/) | QR decomposition, Gram-Schmidt orthogonalization | 10 | 10 | 10 |
| [D6](https://beliavsky.github.io/fortran-playground/gams/D6/) | Singular value decomposition | 10 | 8 | 8 |
| [D8](https://beliavsky.github.io/fortran-playground/gams/D8/) | Other matrix equations (e.g., AX+XB=C) | 3 | 3 | 3 |
| [D9a1](https://beliavsky.github.io/fortran-playground/gams/D9a1/) | Least squares (L_2) solution | 12 | 11 | 11 |
| [D9b1](https://beliavsky.github.io/fortran-playground/gams/D9b1/) | Least squares (L_2) solution | 2 | 2 | 2 |
| [D9c](https://beliavsky.github.io/fortran-playground/gams/D9c/) | Generalized inverses | 3 | 3 | 3 |
| [E1](https://beliavsky.github.io/fortran-playground/gams/E1/) | Univariate data (curve fitting) | 2 | 1 | 1 |
| [E1a](https://beliavsky.github.io/fortran-playground/gams/E1a/) | Polynomial splines (piecewise polynomials) | 8 | 7 | 7 |
| [E2](https://beliavsky.github.io/fortran-playground/gams/E2/) | Multivariate data (surface fitting) | 2 | 1 | 1 |
| [E2a](https://beliavsky.github.io/fortran-playground/gams/E2a/) | Gridded | 6 | 4 | 4 |
| [E3](https://beliavsky.github.io/fortran-playground/gams/E3/) | Service routines for interpolation | 1 | 1 | 1 |
| [E3a2](https://beliavsky.github.io/fortran-playground/gams/E3a2/) | Derivative evaluation | 2 | 2 | 2 |
| [E3a3](https://beliavsky.github.io/fortran-playground/gams/E3a3/) | Quadrature | 1 | 1 | 1 |
| [F1](https://beliavsky.github.io/fortran-playground/gams/F1/) | Single equation | 1 | 1 | 1 |
| [F1a](https://beliavsky.github.io/fortran-playground/gams/F1a/) | Polynomial | 3 | 3 | 3 |
| [F1b](https://beliavsky.github.io/fortran-playground/gams/F1b/) | Nonpolynomial | 10 | 9 | 9 |
| [F2](https://beliavsky.github.io/fortran-playground/gams/F2/) | System of equations | 4 | 4 | 4 |
| [G1a1a](https://beliavsky.github.io/fortran-playground/gams/G1a1a/) | User provides no derivatives | 1 | 1 | 1 |
| [G1b](https://beliavsky.github.io/fortran-playground/gams/G1b/) | Multivariate | 3 | 3 | 3 |
| [G1b1a](https://beliavsky.github.io/fortran-playground/gams/G1b1a/) | User provides no derivatives | 4 | 2 | 2 |
| [G1b1b](https://beliavsky.github.io/fortran-playground/gams/G1b1b/) | User provides first derivatives | 6 | 6 | 6 |
| [G2](https://beliavsky.github.io/fortran-playground/gams/G2/) | Constrained | 2 | 2 | 2 |
| [G2a](https://beliavsky.github.io/fortran-playground/gams/G2a/) | Linear programming | 1 | 1 | 1 |
| [G2h1a1](https://beliavsky.github.io/fortran-playground/gams/G2h1a1/) | User provides no derivatives | 1 | 1 | 1 |
| [G2h1a2](https://beliavsky.github.io/fortran-playground/gams/G2h1a2/) | User provides first derivatives | 2 | 2 | 2 |
| [G2h3b1b](https://beliavsky.github.io/fortran-playground/gams/G2h3b1b/) | User provides first derivatives of function and constraints | 4 | 4 | 4 |
| [G2i](https://beliavsky.github.io/fortran-playground/gams/G2i/) | Global solution to nonconvex problems | 3 | 3 | 3 |
| [H1](https://beliavsky.github.io/fortran-playground/gams/H1/) | Numerical differentiation | 12 | 11 | 11 |
| [H2](https://beliavsky.github.io/fortran-playground/gams/H2/) | Quadrature (numerical evaluation of definite integrals) | 3 | 1 | 1 |
| [H2a1a1](https://beliavsky.github.io/fortran-playground/gams/H2a1a1/) | Automatic (user need only specify required accuracy) | 3 | 3 | 3 |
| [H2a1b2](https://beliavsky.github.io/fortran-playground/gams/H2a1b2/) | Nonautomatic | 4 | 4 | 4 |
| [H2a2a1](https://beliavsky.github.io/fortran-playground/gams/H2a2a1/) | Automatic (user need only specify required accuracy) | 5 | 5 | 5 |
| [H2a2b2](https://beliavsky.github.io/fortran-playground/gams/H2a2b2/) | Nonautomatic | 1 | 1 | 1 |
| [H2a3a1](https://beliavsky.github.io/fortran-playground/gams/H2a3a1/) | Automatic (user need only specify required accuracy) | 1 | 1 | 1 |
| [H2b1a1](https://beliavsky.github.io/fortran-playground/gams/H2b1a1/) | Automatic (user need only specify required accuracy) | 3 | 1 | 1 |
| [H2b1a2](https://beliavsky.github.io/fortran-playground/gams/H2b1a2/) | Nonautomatic | 1 | 1 | 1 |
| [H2c](https://beliavsky.github.io/fortran-playground/gams/H2c/) | Service routines (e.g., compute weights and nodes for quadrature formulas) | 6 | 6 | 6 |
| [I](https://beliavsky.github.io/fortran-playground/gams/I/) | Differential and integral equations | 1 | 1 | 1 |
| [I1](https://beliavsky.github.io/fortran-playground/gams/I1/) | Ordinary differential equations (ODE''s) | 6 | 5 | 5 |
| [I1a1a](https://beliavsky.github.io/fortran-playground/gams/I1a1a/) | One-step methods (e.g., Runge-Kutta) | 9 | 9 | 9 |
| [I1a1b](https://beliavsky.github.io/fortran-playground/gams/I1a1b/) | Multistep methods (e.g., Adams predictor-corrector) | 1 | 1 | 1 |
| [I1a2](https://beliavsky.github.io/fortran-playground/gams/I1a2/) | Stiff and mixed algebraic- differential equations | 4 | 4 | 4 |
| [I1b](https://beliavsky.github.io/fortran-playground/gams/I1b/) | Multipoint boundary value problems | 2 | 1 | 1 |
| [I2](https://beliavsky.github.io/fortran-playground/gams/I2/) | Partial differential equations | 7 | 4 | 4 |
| [I2b1a1a](https://beliavsky.github.io/fortran-playground/gams/I2b1a1a/) | Rectangular domain (or topologically rectangular in the coordinate system) | 1 | 1 | 1 |
| [J](https://beliavsky.github.io/fortran-playground/gams/J/) | Integral transforms | 1 | 1 | 1 |
| [J1](https://beliavsky.github.io/fortran-playground/gams/J1/) | Trigonometric transforms including fast Fourier transforms | 4 | 4 | 4 |
| [J1a1](https://beliavsky.github.io/fortran-playground/gams/J1a1/) | Real | 2 | 2 | 2 |
| [J1a2](https://beliavsky.github.io/fortran-playground/gams/J1a2/) | Complex | 3 | 3 | 3 |
| [J1a3](https://beliavsky.github.io/fortran-playground/gams/J1a3/) | Sine and cosine transforms | 3 | 3 | 3 |
| [J2](https://beliavsky.github.io/fortran-playground/gams/J2/) | Convolutions | 2 | 2 | 2 |
| [K](https://beliavsky.github.io/fortran-playground/gams/K/) | Approximation | 6 | 5 | 5 |
| [K1](https://beliavsky.github.io/fortran-playground/gams/K1/) | Least squares (L-2) approximation | 1 | 1 | 1 |
| [L1a1a](https://beliavsky.github.io/fortran-playground/gams/L1a1a/) | Location | 8 | 6 | 6 |
| [L1a1b](https://beliavsky.github.io/fortran-playground/gams/L1a1b/) | Dispersion | 4 | 4 | 4 |
| [L1a1c](https://beliavsky.github.io/fortran-playground/gams/L1a1c/) | Shape | 4 | 4 | 4 |
| [L1a1d](https://beliavsky.github.io/fortran-playground/gams/L1a1d/) | Frequency, cumulative frequency | 1 | 1 | 1 |
| [L1c1b](https://beliavsky.github.io/fortran-playground/gams/L1c1b/) | Covariance, correlation | 6 | 6 | 6 |
| [L2c](https://beliavsky.github.io/fortran-playground/gams/L2c/) | Subset | 1 | 1 | 1 |
| [L4](https://beliavsky.github.io/fortran-playground/gams/L4/) | Elementary data analysis | 1 | 1 | 1 |
| [L5a1b](https://beliavsky.github.io/fortran-playground/gams/L5a1b/) | Beta, binomial | 3 | 3 | 3 |
| [L5a1c](https://beliavsky.github.io/fortran-playground/gams/L5a1c/) | Cauchy, chi-squared | 1 | 1 | 1 |
| [L5a1e](https://beliavsky.github.io/fortran-playground/gams/L5a1e/) | Error function, exponential, extreme value | 2 | 2 | 2 |
| [L5a1g](https://beliavsky.github.io/fortran-playground/gams/L5a1g/) | Gamma, general, geometric | 2 | 2 | 2 |
| [L5a1n](https://beliavsky.github.io/fortran-playground/gams/L5a1n/) | Negative binomial, normal | 3 | 3 | 3 |
| [L5a1u](https://beliavsky.github.io/fortran-playground/gams/L5a1u/) | Uniform | 4 | 4 | 4 |
| [L6](https://beliavsky.github.io/fortran-playground/gams/L6/) | Random number generation | 2 | 2 | 2 |
| [L6a21](https://beliavsky.github.io/fortran-playground/gams/L6a21/) | Uniform (continuous, discrete), uniform order statistics | 5 | 4 | 4 |
| [L6c](https://beliavsky.github.io/fortran-playground/gams/L6c/) | Service routines (e.g., seed) | 2 | 1 | 1 |
| [L8](https://beliavsky.github.io/fortran-playground/gams/L8/) | Regression | 3 | 2 | 2 |
| [L10a2a](https://beliavsky.github.io/fortran-playground/gams/L10a2a/) | Summary statistics | 1 | 1 | 1 |
| [L13](https://beliavsky.github.io/fortran-playground/gams/L13/) | Covariance structure models | 1 | 1 | 1 |
| [L13b](https://beliavsky.github.io/fortran-playground/gams/L13b/) | Principal components analysis | 2 | 0 | 0 |
| [M](https://beliavsky.github.io/fortran-playground/gams/M/) | Simulation, stochastic modeling | 1 | 1 | 1 |
| [N1](https://beliavsky.github.io/fortran-playground/gams/N1/) | Input, output | 16 | 12 | 12 |
| [N2](https://beliavsky.github.io/fortran-playground/gams/N2/) | Bit manipulation | 3 | 3 | 3 |
| [N3](https://beliavsky.github.io/fortran-playground/gams/N3/) | Character manipulation | 19 | 16 | 16 |
| [N4](https://beliavsky.github.io/fortran-playground/gams/N4/) | Storage management (e.g., stacks, heaps, trees) | 14 | 14 | 14 |
| [N5](https://beliavsky.github.io/fortran-playground/gams/N5/) | Searching | 15 | 4 | 4 |
| [N6](https://beliavsky.github.io/fortran-playground/gams/N6/) | Sorting | 8 | 7 | 7 |
| [N6a1b](https://beliavsky.github.io/fortran-playground/gams/N6a1b/) | Real | 2 | 2 | 2 |
| [N6a2b](https://beliavsky.github.io/fortran-playground/gams/N6a2b/) | Real | 1 | 1 | 1 |
| [P](https://beliavsky.github.io/fortran-playground/gams/P/) | Computational geometry | 11 | 8 | 8 |
| [Q](https://beliavsky.github.io/fortran-playground/gams/Q/) | Graphics | 6 | 1 | 1 |
| [R](https://beliavsky.github.io/fortran-playground/gams/R/) | Service routines | 9 | 9 | 9 |
| [R1](https://beliavsky.github.io/fortran-playground/gams/R1/) | Machine-dependent constants | 1 | 1 | 1 |
| [R2](https://beliavsky.github.io/fortran-playground/gams/R2/) | Error checking (e.g., check monotonicity) | 6 | 3 | 3 |
| [R3](https://beliavsky.github.io/fortran-playground/gams/R3/) | Error handling | 2 | 1 | 1 |
| [S](https://beliavsky.github.io/fortran-playground/gams/S/) | Software development tools | 6 | 6 | 6 |
| [S3](https://beliavsky.github.io/fortran-playground/gams/S3/) | Dynamic program analysis tools | 4 | 4 | 4 |
| [Z](https://beliavsky.github.io/fortran-playground/gams/Z/) | Other | 1 | 1 | 1 |

See the [numerical review](gams-numerical.md) for named procedures and pinned source evidence, and [classification review](fpm-gams.md) for package assignments. Classes with reviewed procedures and zero checked drivers are a useful next-driver queue. The numerical review also lists discovery assignments without matching procedure records.

## Maintenance

This page is regenerated from the same classifications, driver manifest and successful verification reports used by the playground and portable catalog. It is checked by:

```text
python xpackage_gams.py
python xpackage_gams.py --check
```
