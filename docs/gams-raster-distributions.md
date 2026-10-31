# Checked software raster graphics and seeded distributions

These Q and L6 drivers passed the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, reusing existing package libraries. Only their mains and executables were compiled. The [verification report](gams-raster-distributions-validation.json) records pins, source hashes and actual output. GAMS categories are not exhausted.

## Exact raster pixels and PNG round trip: fortran-sdl2 (Q)

An 85x65, 32-bit software surface uses explicit RGB masks and a known background color. Four rectangles overlap and extend beyond the upper-left and lower-right edges. A native loop applies independent half-open coordinate tests in drawing order and forms the expected packed pixels with integer shifts and masks, without calling SDL color mapping. All 5525 RGB pixels must agree exactly, including backgrounds, edges, clipping and overwritten regions.

The surface is exported as PNG, loaded through IMG_Load and converted to the original pixel format. Every pixel is checked again: 11050 exact comparisons in total. A native stream read independently verifies the PNG signature, IHDR chunk tag and big-endian dimensions. The generated PNG was returned as a browser artifact and visually reviewed:

![Verified overlapping and clipped rectangles](gams-raster-distributions.png)

The pinned bindings omit IMG_SavePNG; the driver supplies only its standard C declaration. SDL2_image performs the encoding. No display server, window, event loop or video initialization is used. The author surface/pixel examples were reviewed for interfaces; this drawing and its reference fixture are independently specified. Only RGB content is checked. Alpha blending, hardware rendering, interactive graphics, other codecs and the remaining SDL subsystems are outside this driver.

## Fixed-seed distribution checks: rng-fortran (L6)

Three fixed nonzero seeds use freshly allocated generator/replay objects. Each normal and Poisson call must replay exactly with the same seed and call sequence. There are 20000 samples per seed, or 60000 normal and 60000 Poisson samples, excluding replay calls. The normal mean must be within 0.04 of zero, and its second moment within 0.08 of one. Poisson rates 0.5,2,8 use analytic mean lambda, centered second moment lambda and zero probability exp(-lambda). Their respective absolute tolerances are 0.04*max(1,lambda), 0.12*max(1,lambda) and 0.02. Normal outputs must be finite and Poisson counts nonnegative.

For radii 0.25,1,3, a further 1000 circle and 1000 sphere samples per fixture must replay exactly and have normalized squared norm within 2e-12 of one. Normalized coordinate means must be within 0.15 of zero; second moments must be within 0.12 of 1/2 for the circle and 1/3 for the sphere. The analytic moments are independent references, but these deliberately broad, fixed-seed smoke checks do not certify statistical quality or cryptographic safety. They are not a general hypothesis-testing suite.

Fresh allocations avoid the known source behavior where set_seed does not clear a cached second normal after an odd normal() call. That issue remains unresolved; this driver does not verify such reseeding. All tested Poisson rates use the small-rate branch; rates >=10 and its rejection sampler are not verified. Parallel use, jump independence, extreme rates, all-zero seeds and other distribution routines are also outside this example. The author example was reviewed for API usage; no upstream sampling code is copied.

## Checked links and actual output

These independent API consumers have their own MIT notice; upstream package licenses remain separate. Loading a link does not submit a job.

### sdl-raster-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=fortran-sdl2&example=gams-sdl-raster-reference) / [Driver source](../fpm_catalog/gams-drivers/sdl-raster-reference.f90) / [Pinned procedure](https://github.com/interkosmos/fortran-sdl2/blob/cac974790420ba757c17f88678e66b01500319e7/src/sdl2.f90#L1) / [Author example/test](https://github.com/interkosmos/fortran-sdl2/blob/cac974790420ba757c17f88678e66b01500319e7/examples/alpha.f90)

```text
85x65 software surface: four overlapping/clipped rectangles and five known colors.
11050 exact pixel references checked before and after PNG save/load.
Native PNG signature/dimensions checked; generated image is available for browser display.
PASS sdl-raster-reference
```

### rng-distributions-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=rng-fortran&example=gams-rng-distributions-reference) / [Driver source](../fpm_catalog/gams-drivers/rng-distributions-reference.f90) / [Pinned procedure](https://github.com/jannisteunissen/rng_fortran/blob/5ead95f436323d07fc82acc3613f66550947f256/m_random.f90#L1) / [Author example/test](https://github.com/jannisteunissen/rng_fortran/blob/5ead95f436323d07fc82acc3613f66550947f256/example.f90)

```text
Rate= 0.50 normal mean/second moment=  -0.00522   1.00266
Poisson mean/centered moment/zero mass=   0.49980   0.51310   0.61130
Radius= 0.25 maximum normalized norm error=  4.4409E-16
Rate= 2.00 normal mean/second moment=  -0.00712   0.99522
Poisson mean/centered moment/zero mass=   1.98885   1.96335   0.13530
Radius= 1.00 maximum normalized norm error=  4.4409E-16
Rate= 8.00 normal mean/second moment=   0.00521   1.00284
Poisson mean/centered moment/zero mass=   7.99060   7.91710   0.00040
Radius= 3.00 maximum normalized norm error=  6.6613E-16
60000 normal and 60000 Poisson samples, each replayed exactly with fresh seeded objects.
3000 circle and 3000 sphere samples: exact replay, analytic norms and broad coordinate moments.
Fixed-seed smoke checks do not certify statistical quality or cryptographic safety.
PASS rng-distributions-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers sdl-raster-reference rng-distributions-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. If the graphics fixture changes, refresh its saved PNG preview from the successful sandbox artifact. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
