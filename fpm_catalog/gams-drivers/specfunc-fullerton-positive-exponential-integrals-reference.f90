! Independent MIT consumer; see licenses/fullerton-functions-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: wp=>real64
   use ieee_arithmetic, only: ieee_is_finite
   use specfunc_fullerton, only: &
      integral_e1, integral_en
   implicit none
   real(wp),parameter :: inputs(*)=[ &
      0.00390625_wp, 0.125_wp, 0.5_wp, 1.0_wp, 2.0_wp, 3.0_wp, 4.0_wp, 8.0_wp, 16.0_wp, 0.125_wp, 0.125_wp, &
      0.125_wp, 0.125_wp, 0.125_wp, 0.5_wp, 0.5_wp, 0.5_wp, 0.5_wp, 0.5_wp, 1.0_wp, 1.0_wp, 1.0_wp, 1.0_wp, 1.0_wp, &
      2.0_wp, 2.0_wp, 2.0_wp, 2.0_wp, 2.0_wp]
   real(wp),parameter :: references(*)=[ &
      4.97186421818970934_wp, 1.62342564058416879_wp, 0.559773594776160812_wp, 0.219383934395520274_wp, &
      0.0489005107080611196_wp, 0.0130483810941970374_wp, 0.00377935240984890648_wp, 0.0000376656228439249018_wp, &
      6.64048724944104279e-9_wp, 1.62342564058416879_wp, 0.679568697511574304_wp, 0.398775407697824307_wp, &
      0.277549992207455788_wp, 0.211950788389665857_wp, 0.559773594776160812_wp, 0.326643862324553018_wp, &
      0.221604364275178457_wp, 0.165242825858348065_wp, 0.130977311695864848_wp, 0.219383934395520274_wp, &
      0.148495506775922048_wp, 0.109691967197760137_wp, 0.0860624913245607283_wp, 0.0704542374617203983_wp, &
      0.0489005107080611196_wp, 0.0375342618204904528_wp, 0.0301333797978158932_wp, 0.0250228412136603018_wp, &
      0.0213224002023230221_wp]
   integer,parameter :: which(*)=[ &
      1,1,1,1,1,1,1,1,1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2]
   integer,parameter :: orders(*)=[ &
      1,1,1,1,1,1,1,1,1,1,2,3,4,5,1,2,3,4,5,1,2,3,4,5,1,2,3,4,5]
   real(wp) :: actual,expected,relative_error,maximum_error
   integer :: i
   maximum_error=0
   do i=1,size(inputs)
      select case(which(i))
      case(1)
         actual=real(integral_e1(real(inputs(i))),wp)
      case(2)
         actual=real(integral_en(orders(i),real(inputs(i))),wp)
      case default
         error stop 'Unknown function selector'
      end select
      expected=references(i)
      if(.not.ieee_is_finite(actual)) error stop 'Nonfinite special function'
      relative_error=abs(actual-expected)/max(abs(expected),1.e-30_wp)
      if(relative_error>5.e-5_wp) then
         print '(a,i0,a,es16.8,a,es16.8,a,es16.8)', 'Case ',i,': x=',inputs(i), &
            ' actual=',actual,' expected=',expected
         error stop 'Independent high-precision reference'
      end if
      maximum_error=max(maximum_error,relative_error)
   end do
   print '(a,i0)', 'Default REAL32 function comparisons with independent references: ',size(inputs)
   print '(a,es12.4)', 'Maximum relative error (reference floor 1e-30): ',maximum_error
   print '(a)', 'PASS specfunc-fullerton-positive-exponential-integrals-reference'
end program
