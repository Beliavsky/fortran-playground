! Example: Numerical: integration by the trapezoidal rule
! Try doubling n; how does the error change?
program trapezoidal_integration
   use, intrinsic :: iso_fortran_env, only: real64
   implicit none
   integer, parameter :: n = 100
   real(real64) :: pi, h, integral
   integer :: i
   pi = acos(-1.0_real64)
   h = pi/n
   integral = 0.0_real64 ! sin(0) and sin(pi) have zero endpoint contribution.
   do i = 1, n-1
      integral = integral + sin(i*h)
   end do
   integral = integral*h
   print '(a,f14.10)', 'Integral of sin from 0 to pi: ', integral
   print '(a,f14.10)', 'Exact integral: ', 2.0_real64
   print '(a,es14.6)', 'Absolute error: ', abs(integral-2)
end program trapezoidal_integration
