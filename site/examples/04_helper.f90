! Example: python_mod mean
program main
   use, intrinsic :: iso_fortran_env, only: real64
   use python_mod, only: mean
   implicit none
   real(real64) :: x(3) = [1.0_real64, 2.0_real64, 3.0_real64]
   print *, mean(x)
end program main
