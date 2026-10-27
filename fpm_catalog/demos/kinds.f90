program main
   use kinds, only: rk, ik, rk64
   implicit none
   real(rk) :: x
   integer(ik) :: n
   x = sqrt(2.0_rk)
   n = 100_ik
   if (precision(1.0_rk64) < 15) error stop 'insufficient double precision'
   if (abs(x*x-2.0_rk) > 10*epsilon(x)) error stop 'incorrect square root'
   print *, 'Working real precision:', precision(x), 'digits'
   print *, 'Integer storage:', storage_size(n), 'bits'
   print *, 'PASS kinds'
end program
