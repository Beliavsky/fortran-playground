! Independent MIT consumer; see licenses/fullerton-functions-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: wp=>real64
   use ieee_arithmetic, only: ieee_is_finite
   use specfunc_fullerton, only: &
      integral_dawson, dawson_prime
   implicit none
   real(wp),parameter :: inputs(*)=[ &
      -8.0_wp, -8.0_wp, -4.0_wp, -4.0_wp, -2.0_wp, -2.0_wp, -1.0_wp, -1.0_wp, -0.5_wp, -0.5_wp, -0.125_wp, &
      -0.125_wp, 0.0_wp, 0.0_wp, 0.125_wp, 0.125_wp, 0.5_wp, 0.5_wp, 1.0_wp, 1.0_wp, 2.0_wp, 2.0_wp, 3.0_wp, 3.0_wp, &
      4.0_wp, 4.0_wp, 8.0_wp, 8.0_wp]
   real(wp),parameter :: references(*)=[ &
      -0.0630001987075533879_wp, -0.00800317932085420671_wp, -0.129348001236005116_wp, -0.0347840098880409247_wp, &
      -0.301340388923791966_wp, -0.205361555695167864_wp, -0.538079506912768419_wp, -0.0761590138255368383_wp, &
      -0.424436383502022296_wp, 0.575563616497977704_wp, -0.123706018482839734_wp, 0.969073495379290067_wp, 0.0_wp, &
      1.0_wp, 0.123706018482839734_wp, 0.969073495379290067_wp, 0.424436383502022296_wp, 0.575563616497977704_wp, &
      0.538079506912768419_wp, -0.0761590138255368383_wp, 0.301340388923791966_wp, -0.205361555695167864_wp, &
      0.178271030610558287_wp, -0.0696261836633497241_wp, 0.129348001236005116_wp, -0.0347840098880409247_wp, &
      0.0630001987075533879_wp, -0.00800317932085420671_wp]
   integer,parameter :: which(*)=[ &
      1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2]
   integer,parameter :: orders(*)=[ &
      0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
   real(wp) :: actual,expected,relative_error,maximum_error
   integer :: i
   maximum_error=0
   do i=1,size(inputs)
      select case(which(i))
      case(1)
         actual=real(integral_dawson(real(inputs(i))),wp)
      case(2)
         actual=real(dawson_prime(real(inputs(i))),wp)
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
   print '(a)', 'PASS specfunc-fullerton-dawson-values-derivatives-reference'
end program
