! Independent MIT consumer; see licenses/fullerton-functions-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: wp=>real64
   use ieee_arithmetic, only: ieee_is_finite
   use specfunc_fullerton, only: &
      integral_spence
   implicit none
   real(wp),parameter :: inputs(*)=[ &
      -8.0_wp, -4.0_wp, -2.0_wp, -1.0_wp, -0.5_wp, -0.125_wp, 0.0_wp, 0.125_wp, 0.5_wp, 0.75_wp, 0.875_wp, 1.0_wp]
   real(wp),parameter :: references(*)=[ &
      -3.68567600075740637_wp, -2.36993979699836583_wp, -1.43674636688368095_wp, -0.822467033424113218_wp, &
      -0.448414206923646202_wp, -0.121296628722726479_wp, 0.0_wp, 0.129139860109953406_wp, 0.582240526465012506_wp, &
      0.978469392930306104_wp, 1.23812348179648023_wp, 1.64493406684822644_wp]
   integer,parameter :: which(*)=[ &
      1,1,1,1,1,1,1,1,1,1,1,1]
   integer,parameter :: orders(*)=[ &
      0,0,0,0,0,0,0,0,0,0,0,0]
   real(wp) :: actual,expected,relative_error,maximum_error
   integer :: i
   maximum_error=0
   do i=1,size(inputs)
      select case(which(i))
      case(1)
         actual=real(integral_spence(real(inputs(i))),wp)
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
   print '(a)', 'PASS specfunc-fullerton-real-dilogarithm-reference'
end program
