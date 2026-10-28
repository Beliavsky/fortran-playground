# rational-approximation
[![Language](https://img.shields.io/badge/-Fortran-734f96?logo=fortran&logoColor=white)](https://github.com/topics/fortran)
[![CI](https://github.com/edvinolo/rational-approximation/actions/workflows/CI.yml/badge.svg)](https://github.com/edvinolo/rational-approximation/actions/workflows/CI.yml)
[![GitHub last commit (branch)](https://img.shields.io/github/last-commit/edvinolo/rational-approximation/main)](https://github.com/edvinolo/rational-approximation/commits/main/)

This is a Fortran library for rational approximation of functions. The library can be built using the Fortran Package Manager (fpm). Multiple precisions are supported using the fypp preprocessing tool. Both real and complex types are supported.

## Currently supported interpolation schemes
- ```thiele_interp``` Interpolates using Thiele's interpolation formula.
- ```MTT_interp``` Finds an interpolant using the modified Thacher-Tukey (MTT) algorithm.

## Currently supported approximation schemes
- ```pade``` Computes a Padé approximant of specified type from Taylor coefficients. The implementation uses the SVD-based robust Padé algorithm of Gonnet, Güttel, and Trefethen (SIAM Review 55, 1, 101-117, 2013).

## Building the library
The library can be built with the ```fpm build``` command.

## Running the tests
The suite of tests can be run with the ```fpm test``` command.

## Examples
The examples can be found in the ```example``` directory. 

To run all of them, do: ```fpm run --example```. 

To run a specific example, instead do: ```fpm run --example Name_of_example```.

The current list of examples is:
- ```thiele_sin``` Computes an interpolation of sin for real and complex arguments using Thiele's interpolation formula (```thiele_interp```)
- ```MTT_cos``` Computes an interpolation of cos for real and complex arguments using the MTT algorithm (```MTT_interp```). Also checks one of the early stopping conditions of the algorithm.
- ```pade_exp``` Computes a [3/2] Padé approximant of exp(x) using the robust Padé algorithm. Compares with actual values.

## Supported compilers
The library is tested with the following compilers and OS's on the default branch:

Name | Version | Platform | Architecture
--- | --- | --- | ---
Intel oneAPI LLVM | 2024.1, 2025.2, 2025.3 | Ubuntu 24.04.3 LTS | x86_64
Intel oneAPI classic | 2021.10 | Ubuntu 24.04.3 LTS | x86_64
Intel oneAPI classic | 2021.10 | macOS 15.7.1 (24G231) | x86_64

Other versions may work, but have not been tested at the moment. 

The library uses parameterized derived types (PDTs) with ```kind``` type parameters, which means this must be supported by the compiler you intend to build the library with.

## Using the library
For each supported approximaiton type there are two versions, one for real input data and one for complex. This is indicated by a suffix on the corresponding PDT, ```re``` for real or ```cp``` for complex. If you want to evaluate the interpolant for complex arguments, then you need to use the complex version. The precision is controlled by the PDTs kind type parameter.

For example, to declare a ```MTT_interp``` instance, for ```complex(k)``` data use:
```
MTT_interp_cp(k) :: cmplx_MTT
```

To compute the interpolant for the interpolation points ```x``` and function values ```y```:
```
call cmplx_MTT%init(x,y)
```

To evaluate the interpolant at ```z```:
```
cmplx_MTT%eval(z)
```
Currently, ```z``` can be a scalar or rank 1 array.
