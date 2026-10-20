! Example: Quadratic roots
program main
   use, intrinsic :: iso_fortran_env, only: real64
   implicit none
   real(real64) :: a, b, c, discriminant
   a = 1.0_real64
   b = -3.0_real64
   c = 2.0_real64
   discriminant = b*b - 4*a*c
   print *, (-b + sqrt(discriminant))/(2*a)
   print *, (-b - sqrt(discriminant))/(2*a)
end program main
