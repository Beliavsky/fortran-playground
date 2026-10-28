program demo_iapws
   use iso_fortran_env, only: real64
   use iapws, only: psat, tsat
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   real(real64) :: temperature(3), pressure(3), restored(3)
   ! IAPWS-IF97 Table 35 reference pressures (MPa), temperatures in kelvin.
   real(real64), parameter :: reference(3) = [0.00353658941_real64, 2.63889776_real64, 12.3443146_real64]
   integer :: i

   temperature = [300._real64, 500._real64, 600._real64]
   call psat(temperature, pressure)
   if (.not. all(ieee_is_finite(pressure))) error stop 'Nonfinite saturation pressure'
   if (any(abs(pressure-reference) > 5.e-8_real64)) error stop 'Reference pressure check failed'
   call tsat(pressure, restored)
   if (maxval(abs(restored-temperature)) > 1.e-7_real64) error stop 'Temperature round trip failed'
   print '(a)', 'Temperature (K)    Saturation pressure (MPa)'
   do i = 1, 3
      print '(f12.2,f24.10)', temperature(i), pressure(i)
   end do
   print *, 'PASS iapws'
end program demo_iapws
