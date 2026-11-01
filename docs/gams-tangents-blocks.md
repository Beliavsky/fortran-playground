# Checked tangent flows and block-sparse products

These I1 and D1 drivers passed GNU Fortran 16.2.0 with FPM 0.12.0 in the restricted hosted sandbox. Existing libraries were reused; only mains and executables were compiled. The [verification report](gams-tangents-blocks-validation.json) retains pins, source hashes and complete output. GAMS categories are not exhausted.

## FATODE coupled decay and full tangent derivatives (I1)

The independent consumer integrates y1_prime=-k*y1+c*y2, y2_prime=-k*y2, k_prime=0, c_prime=0. The last two constant states expose derivatives with respect to rate k and coupling c through the same tangent-linear interface as initial-condition derivatives. Four identity columns initialize the tangent matrix. The supplied analytical Jacobian is explicitly selected and tangent variables participate in adaptive error control. This verifies the explicit ERK/TLM implementation compiled by the existing wrapper; no bundled binary or changed numerical library is used.

For elapsed time tau and initial physical states a,b, let E=exp(-k*tau). The exact final state is [E*(a+c*b*tau), E*b, k, c]. The exact flow-derivative rows, with columns for initial a,b,k,c, are [E,c*tau*E,-tau*y1,b*tau*E], [0,E,-tau*y2,0], [0,0,1,0] and [0,0,0,1]. These elementary formulas give independent endpoint references without finite differencing or another ODE solver.

Methods 4 (Dopri5) and 6 (Dopri853), rates [0.25,2,8], couplings [-1.5,0,2], durations [-1,-0.125,0.125,1,2], initial physical states [(1,0.5),(-0.75,1.25),(0,0)] and time origins [0,0.75] give 540 integrations. This includes forward/backward evolution, coupled and uncoupled states, signed and zero initial states, and translation of the time origin. All 2,160 state entries and 8,640 tangent entries are checked, including the constant-state derivative rows.

Absolute/relative tolerances are 1e-12/1e-10 for both state and tangent arrays, with a 10,000-step cap. Return status must be exactly 1, callbacks and accepted steps must be present, and all output values must be finite. Exit time must agree with the requested endpoint within 64*epsilon(real64)*max(1,abs(endpoint)). Constant k,c states must be unchanged exactly. Each state/tangent entry error divided by 1+abs(analytic_entry) must be <=2e-7.

The saved maximum state and tangent discrepancies were 4.43326e-10 and 7.23387e-10. Each callback type was actually invoked 535,978 times. These counts describe this suite and are not a performance comparison. Finite-difference Jacobians, the other ERK methods, implicit/stiff integrators, adjoints, sparse variants and arbitrary nonlinear systems remain unverified. I1 is the maintained broad ODE mapping; these checks do not establish a narrower stiff-solver class.

## DBCSR irregular block products and accumulation (D1)

The independent serial real64 consumer checks C_out=alpha*op(A)*op(B)+beta*C_in, comparing every entry against scalar loops. No MATMUL, BLAS call or other sparse library supplies the reference. Operator dimensions (m,k,n) are (4,3,4) and (3,6,5). Their block partitions are respectively m=[1,2,1], k=[2,1], n=[1,3] and m=[2,1], k=[1,3,2], n=[2,1,2], exercising unequal block sizes and rectangular operands/results. Stored arrays/partitions are transposed when a T operand is requested.

Each layout uses four data patterns: full dyadic values, block-sparse dyadic values, full non-dyadic values, and a structurally empty A. Entry formulas before applying block masks are A_ij=(2*i-3*j+1)/dA, B_ij=(3*i+j-2)/dB and C_ij=(i-2*j+3)/dC. Dyadic denominators are all 8; non-dyadic denominators are 7,11,13. In the sparse pattern, A keeps blocks with even row+column block index, while B removes blocks for which 2*row_block+column_block is divisible by 3. C_in contains its full formula. Zero blocks are not inserted.

Both layouts, four patterns and every NN/NT/TN/TT pair give 32 products and 496 scalar reference entries. The six alpha/beta pairs [(1,0),(-1.25,0.5),(0,-1),(2,0),(0,0),(0.5,1)] cycle through those fixtures in order. They are not an extra Cartesian dimension, so not every scalar pair is tested with every matrix. This covers overwriting C, scaling an existing C, negative accumulation, zero multipliers and structurally empty input.

Filtering is explicitly set to zero. The consumer reconstructs stored C blocks, treating missing blocks as zeros and honoring returned block-transposition flags. Every entry must be finite. Absolute discrepancy divided by 1+abs(beta*C_in_ij)+sum_h(abs(alpha*A_ih*B_hj)) must be <=128*epsilon(real64)*(k+2). The maximum normalized discrepancy was 1.91702e-16. Serial nonsymmetric real64 CPU operation is verified here; MPI, OpenMP, GPU, accelerators, symmetry storage, complex arithmetic and general sparse-pattern behavior remain unverified.

The [288-case Cartesian draft](gams-candidates/dbcsr-output-limit/README.md) compiled but was stopped by the 200,000-byte output limit because the checked library build repeatedly reported array temporaries. It is not counted as numerical verification. The successful selected driver supplies contiguous copied blocks and preserves its remaining native diagnostics in the proof (about 105 KB of run stderr). No diagnostics are suppressed and no backend limit or library source is changed. An earlier [read-only unpacking handle](gams-candidates/dbcsr-consumer-intent/README.md) was a consumer interface error, corrected to intent(inout) without changing the reference or tolerance.

## Sources, licenses and actual output

Pinned APIs, implementations and author examples were reviewed before writing the independent consumers. No upstream implementation or example bodies are copied. The drivers have their own MIT notice; upstream FATODE and DBCSR license terms remain separate. Loading a driver does not submit a job.

### fatode-tangent-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=fatode&example=gams-fatode-tangent-reference) / [Driver source](../fpm_catalog/gams-drivers/fatode-tangent-reference.f90) / [Pinned procedure](https://github.com/ComputationalScienceLaboratory/FATODE/blob/3f237c49bd377644a597c2a49ae5a83f090bfab5/TLM/ERK_TLM/ERK_TLM_f90_Integrator.F90#L1) / [Author test](https://github.com/ComputationalScienceLaboratory/FATODE/blob/3f237c49bd377644a597c2a49ae5a83f090bfab5/EXAMPLES/swe/SWE_ERK_TLM/swe2D_erk_tlm_dr.F90)

```text
Tangent integrations: 540; state entries: 2160; derivative entries: 8640
Actual RHS and analytic-Jacobian callbacks:       535978      535978
Maximum normalized state and tangent errors:    4.43326E-10   7.23387E-10
Dopri5/Dopri853, forward/backward time, full initial-state/parameter derivatives checked.
PASS fatode-tangent-reference
```

### dbcsr-products-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=dbcsr&example=gams-dbcsr-products-reference) / [Driver source](../fpm_catalog/gams-drivers/dbcsr-products-reference.f90) / [Pinned procedure](https://github.com/cp2k/dbcsr/blob/cd6f522ec5005da8c59d2883975a89a2da607eac/src/mm/dbcsr_multiply_api.F#L1) / [Author test](https://github.com/cp2k/dbcsr/blob/cd6f522ec5005da8c59d2883975a89a2da607eac/examples/dbcsr_example_3.F)

```text
Block-sparse products: 32; scalar reference entries: 496
Maximum normalized product error:    1.91702E-16
All N/T flag pairs, irregular blocks, sparse/empty inputs and alpha/beta accumulation checked.
Serial real64 CPU build only; MPI, accelerators and symmetry storage unverified.
PASS dbcsr-products-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers fatode-tangent-reference dbcsr-products-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
