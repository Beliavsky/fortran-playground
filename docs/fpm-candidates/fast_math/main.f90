! An accuracy demonstration, not a timing benchmark. Accumulate real32
! values and compare with an exactly representable real64 reference.
program demo_fast_math
   use iso_fortran_env, only: real32,real64
   use fast_math, only: fsum,fsum_kahan,fprod_kahan
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   real(real32) :: x(10001),ones(10001),ordinary,chunked,compensated,dot
   real(real64) :: reference
   x = 1; x(1) = 1e8_real32; ones = 1
   reference = sum(real(x,real64))
   ordinary = sum(x)
   chunked = fsum(x)
   compensated = fsum_kahan(x)
   dot = fprod_kahan(x,ones)
   if (.not. all(ieee_is_finite([ordinary,chunked,compensated,dot]))) error stop 'Nonfinite sum'
   if (abs(real(compensated,real64)-reference)>8.0_real64) error stop 'Compensated sum differs'
   if (abs(real(dot,real64)-reference)>8.0_real64) error stop 'Compensated dot product differs'
   print '(a,f16.1)', 'Real64 reference: ',reference
   print '(a)', 'Real32 method            Result       Absolute error'
   print '(a,2f18.1)', 'Intrinsic SUM  ',ordinary,abs(real(ordinary,real64)-reference)
   print '(a,2f18.1)', 'Chunked sum    ',chunked,abs(real(chunked,real64)-reference)
   print '(a,2f18.1)', 'Compensated sum',compensated,abs(real(compensated,real64)-reference)
   print '(a,2f18.1)', 'Compensated dot',dot,abs(real(dot,real64)-reference)
   print '(a)', 'PASS fast_math'
end program
