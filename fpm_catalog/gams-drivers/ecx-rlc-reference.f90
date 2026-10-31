! Independent API consumer; MIT: licenses/circuits-beta-drivers-MIT.txt.
program rlc_reference
   use, intrinsic :: iso_fortran_env, only: dp => real64, int32
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   use ecx, only: z
   implicit none
   real(dp), parameter :: resistances(*) = [1._dp,10._dp,100._dp]
   real(dp), parameter :: capacitances(*) = [.001_dp,.01_dp],inductances(*) = [.01_dp,.1_dp]
   real(dp) :: omega(18),resistance,capacitance,inductance,t,max_error
   complex(dp) :: resistor(18),capacitor(18),inductor(18),series(18),parallel(18),expected
   integer :: i,j,k,n,circuits,frequencies
   max_error = 0._dp
   circuits = 0
   frequencies = 0
   do i = 1,size(resistances)
      resistance = resistances(i)
      do j = 1,size(capacitances)
         capacitance = capacitances(j)
         do k = 1,size(inductances)
            inductance = inductances(k)
            omega(:17) = [(scale(1._dp,n),n=-8,8)]
            omega(18) = 1/sqrt(inductance*capacitance)
            call element(resistance,'R',resistor)
            call element(capacitance,'C',capacitor)
            call element(inductance,'L',inductor)
            series = resistor+capacitor+inductor
            parallel = resistor*capacitor/(resistor+capacitor)
            do n = 1,size(omega)
               call check(resistor(n),cmplx(resistance,0._dp,dp))
               call check(capacitor(n),cmplx(0._dp,-1/(omega(n)*capacitance),dp))
               call check(inductor(n),cmplx(0._dp,omega(n)*inductance,dp))
               expected = cmplx(resistance,omega(n)*inductance-1/(omega(n)*capacitance),dp)
               call check(series(n),expected)
               t = omega(n)*resistance*capacitance
               expected = cmplx(resistance/(1+t*t),-resistance*t/(1+t*t),dp)
               call check(parallel(n),expected)
            end do
            if (abs(aimag(series(18))) > 1.e-12_dp*max(1._dp,resistance)) error stop 'series resonance'
            if (abs(abs(series(18))-resistance) > 1.e-12_dp*max(1._dp,resistance)) &
               error stop 'resonant impedance magnitude'
            circuits = circuits+1
            frequencies = frequencies+size(omega)
         end do
      end do
   end do
   if (circuits /= 12 .or. frequencies /= 216) error stop 'circuit count'
   print '(a)', '12 RLC parameter sets, 216 frequency cases, 648 element impedances checked.'
   print '(a)', 'Series RLC resonance and parallel RC real/imaginary formulas checked.'
   print '(a,es12.4)', 'Maximum complex error / max(1,abs(reference)): ',max_error
   print '(a)', 'PASS ecx-rlc-reference'
contains
   subroutine element(parameter,code,values)
      real(dp), intent(in) :: parameter
      character, intent(in) :: code
      complex(dp), intent(out) :: values(18)
      integer(int32) :: status
      character(:), pointer :: message
      ! The public API requires three parameters even for a one-parameter element.
      call z([parameter,0._dp,0._dp],omega,values,code,status,message)
      if (status /= 0) error stop 'element status'
      if (.not. associated(message)) error stop 'missing element diagnostic'
      if (message /= 'No error') error stop 'element success diagnostic'
   end subroutine element
   subroutine check(actual,reference)
      complex(dp), intent(in) :: actual,reference
      real(dp) :: error
      if (.not. ieee_is_finite(real(actual)) .or. .not. ieee_is_finite(aimag(actual))) &
         error stop 'nonfinite impedance'
      error = abs(actual-reference)/max(1._dp,abs(reference))
      max_error = max(max_error,error)
      if (error > 2.e-13_dp) error stop 'independent circuit reference'
   end subroutine check
end program rlc_reference
