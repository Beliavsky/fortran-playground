program main
   use mt19937_64, only: mt19937
   use iso_fortran_env, only: real64
   implicit none
   type(mt19937) :: generator
   real(real64) :: first, repeated
   call generator%initialize(42)
   first = generator%genrand64_real2()
   call generator%initialize(42)
   repeated = generator%genrand64_real2()
   if (first /= repeated .or. first < 0 .or. first >= 1) error stop 'incorrect generator'
   print *, 'First uniform value for seed 42:', first
   print *, 'PASS mersenne-twister-fortran'
end program main
