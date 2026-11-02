! Independent MIT consumer; see licenses/fullerton-functions-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: wp=>real64
   use ieee_arithmetic, only: ieee_is_finite
   use specfunc_fullerton, only: &
      integral_shi, integral_chi
   implicit none
   real(wp),parameter :: inputs(*)=[ &
      0.00390625_wp, 0.00390625_wp, 0.125_wp, 0.125_wp, 0.375_wp, 0.375_wp, 0.5_wp, 0.5_wp, 1.0_wp, 1.0_wp, 2.0_wp, &
      2.0_wp, 3.0_wp, 3.0_wp, 4.0_wp, 4.0_wp, 8.0_wp, 8.0_wp, 16.0_wp, 16.0_wp]
   real(wp),parameter :: references(*)=[ &
      0.00390625331137067001_wp, -4.96795796487833867_wp, 0.125108557820592727_wp, -1.49831708276357606_wp, &
      0.377942076723128804_wp, -0.368250699513786805_wp, 0.506996749819667196_wp, -0.0527768449564936159_wp, &
      1.05725087537572851_wp, 0.837866940980208241_wp, 2.50156743335497564_wp, 2.45266692264691452_wp, &
      4.9734404758598068_wp, 4.96039209476560976_wp, 9.81732691123303446_wp, 9.81354755882318556_wp, &
      220.189968600230556_wp, 220.189930934607713_wp, 297780.499335421821_wp, 297780.499335415181_wp]
   integer,parameter :: which(*)=[ &
      1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2]
   integer,parameter :: orders(*)=[ &
      0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
   real(wp) :: actual,expected,relative_error,maximum_error
   integer :: i
   maximum_error=0
   do i=1,size(inputs)
      select case(which(i))
      case(1)
         actual=real(integral_shi(real(inputs(i))),wp)
      case(2)
         actual=real(integral_chi(real(inputs(i))),wp)
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
   print '(a)', 'PASS specfunc-fullerton-hyperbolic-integrals-reference'
end program
