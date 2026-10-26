program main
   use iso_fortran_env, only: real64
   use stdlib_stats, only: mean
   implicit none
   real(real64) :: x(4)
   x = [1.0_real64, 2.0_real64, 3.0_real64, 4.0_real64]
   if (abs(mean(x)-2.5_real64) > 1.0e-12_real64) error stop 'incorrect mean'
   print *, 'mean =', mean(x)
   print *, 'PASS stdlib'
end program main
