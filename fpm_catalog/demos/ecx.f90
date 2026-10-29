program series_rc_impedance
   use iso_fortran_env, only: dp => real64, int32
   use ieee_arithmetic, only: ieee_is_finite
   use ecx, only: z
   implicit none
   real(dp), parameter :: resistance=100.0_dp, capacitance=0.001_dp
   real(dp) :: omega(4) = [1.0_dp, 10.0_dp, 100.0_dp, 1000.0_dp]
   complex(dp) :: resistor(4), capacitor(4), impedance(4), expected(4)
   integer(int32) :: status
   character(:), pointer :: message
   integer :: i
   ! ECX expects at least three parameters, even for a one-parameter element.
   call z([resistance,0.0_dp,0.0_dp], omega, resistor, 'R', status, message)
   if (status/=0) then
      print *, message
      error stop 'Resistor calculation failed'
   end if
   call z([capacitance,0.0_dp,0.0_dp], omega, capacitor, 'C', status, message)
   if (status/=0) then
      print *, message
      error stop 'Capacitor calculation failed'
   end if
   impedance = resistor + capacitor
   expected = cmplx(resistance, -1/(omega*capacitance), kind=dp)
   if (.not.all(ieee_is_finite(real(impedance)))) error stop 'Nonfinite real part'
   if (.not.all(ieee_is_finite(aimag(impedance)))) error stop 'Nonfinite imaginary part'
   if (maxval(abs(impedance-expected))>1.e-10_dp) error stop 'RC impedance mismatch'
   print '(a)', 'Series RC circuit: R=100 ohm, C=1 mF'
   print '(a)', '  omega (rad/s)    Re(Z) (ohm)    Im(Z) (ohm)'
   do i=1,size(omega)
      print '(3f15.4)', omega(i), real(impedance(i)), aimag(impedance(i))
   end do
   print *, 'PASS ecx'
end program series_rc_impedance
