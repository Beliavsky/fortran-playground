! Example: Numbers: precision and rounding
! Try replacing 0.1 with 0.5, which has an exact binary representation.
program precision_and_rounding
   use, intrinsic :: iso_fortran_env, only: real32, real64
   implicit none
   real(real32) :: x
   real(real64) :: y
   x = 0.1_real32
   y = 0.1_real64
   print '(a,i0)', 'Decimal precision real32: ', precision(x)
   print '(a,i0)', 'Decimal precision real64: ', precision(y)
   print '(a,es14.6)', 'Machine epsilon real32: ', epsilon(x)
   print '(a,es14.6)', 'Machine epsilon real64: ', epsilon(y)
   print '(a,f22.18)', 'real32 widened to real64: ', real(x,real64)
   print '(a,f22.18)', 'real64 literal: ', y
end program precision_and_rounding
