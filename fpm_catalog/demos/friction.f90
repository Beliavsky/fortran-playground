program demo_friction_curves
   use, intrinsic :: iso_fortran_env, only: real64
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   use friction, only: coulomb_model, stribeck_model
   implicit none
   type(coulomb_model) :: dry
   type(stribeck_model) :: sliding
   real(real64), parameter :: load = 20.0_real64
   real(real64), parameter :: velocities(*) = [-1.0_real64, -0.25_real64, 0.0_real64, 0.25_real64, 1.0_real64]
   real(real64) :: v, fc, fs, expected_c, expected_s, magnitude
   integer :: i

   ! Calling conventions follow the author's friction_model_tests.f90.
   dry%friction_coefficient = 0.3_real64
   sliding%static_friction_coefficient = 0.6_real64
   sliding%coulomb_friction_coefficient = 0.3_real64
   sliding%stribeck_velocity = 0.5_real64
   sliding%viscous_damping = 1.5_real64
   print '(a)', 'Velocity     Coulomb     Stribeck (N)'
   do i = 1, size(velocities)
      v = velocities(i)
      expected_c = 0.0_real64
      expected_s = 0.0_real64
      if (v /= 0.0_real64) then
         expected_c = sign(6.0_real64, v)
         magnitude = 6.0_real64 + 6.0_real64*exp(-4.0_real64*v*v)
         expected_s = sign(magnitude, v) + 1.5_real64*v
      end if
      fc = dry%evaluate(0.0_real64, 0.0_real64, v, load)
      fs = sliding%evaluate(0.0_real64, 0.0_real64, v, load)
      if (.not. ieee_is_finite(fc) .or. .not. ieee_is_finite(fs)) error stop 'nonfinite force'
      if (abs(fc - expected_c) > 1.e-12_real64) error stop 'Coulomb force'
      if (abs(fs - expected_s) > 1.e-12_real64) error stop 'Stribeck force'
      print '(3f12.6)', v, fc, fs
   end do
   if (dry%has_internal_state() .or. sliding%has_internal_state()) error stop 'unexpected internal state'
   print '(a)', 'The library reports signed friction; a force balance must use its chosen sign convention.'
   print '(a)', 'PASS friction'
end program demo_friction_curves
