program demo_rngff
   use iso_fortran_env, only: real64, int32
   use rngff, only: linear_congruential_t
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   type(linear_congruential_t) :: generator, replay
   real(real64) :: u, again, integral, first(5)
   integer :: i

   generator = linear_congruential_t(12345_int32, 67890_int32)
   replay = linear_congruential_t(12345_int32, 67890_int32)
   integral = 0._real64
   do i = 1, 20000
      call generator%next(u)
      call replay%next(again)
      if (.not. ieee_is_finite(u)) error stop 'Nonfinite random value'
      if (u /= again) error stop 'Seeded replay differs'
      if (u < 0._real64 .or. u >= 1._real64) error stop 'Value outside [0,1)'
      if (i <= 5) first(i) = u
      integral = integral + u*u
   end do
   integral = integral/20000
   if (abs(integral-1._real64/3) > 0.015_real64) error stop 'Monte Carlo estimate outside tolerance'
   print '(a,5f11.7)', 'First five draws:', first
   print '(a,f12.7)', 'Monte Carlo integral of x squared on [0,1]: ', integral
   print '(a)', 'The same seeds reproduced all 20000 draws.'
   print *, 'PASS rngff'
end program demo_rngff
