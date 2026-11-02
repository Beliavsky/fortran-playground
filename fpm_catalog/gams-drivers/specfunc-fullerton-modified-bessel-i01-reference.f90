! Independent MIT consumer; see licenses/fullerton-functions-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: wp=>real64
   use ieee_arithmetic, only: ieee_is_finite
   use specfunc_fullerton, only: &
      bessel_i0, bessel_i1
   implicit none
   real(wp),parameter :: inputs(*)=[ &
      -16.0_wp, -16.0_wp, -8.0_wp, -8.0_wp, -4.0_wp, -4.0_wp, -2.0_wp, -2.0_wp, -1.0_wp, -1.0_wp, -0.5_wp, -0.5_wp, &
      -0.125_wp, -0.125_wp, -0.00390625_wp, -0.00390625_wp, 0.0_wp, 0.0_wp, 0.00390625_wp, 0.00390625_wp, 0.125_wp, &
      0.125_wp, 0.5_wp, 0.5_wp, 1.0_wp, 1.0_wp, 2.0_wp, 2.0_wp, 3.0_wp, 3.0_wp, 4.0_wp, 4.0_wp, 8.0_wp, 8.0_wp, &
      16.0_wp, 16.0_wp]
   real(wp),parameter :: references(*)=[ &
      893446.227920105017_wp, -865059.435854839471_wp, 427.564115721804785_wp, -399.873136782560098_wp, &
      11.3019219521363305_wp, -9.75946515370444991_wp, 2.27958530233606727_wp, -1.59063685463732906_wp, &
      1.26606587775200834_wp, -0.565159103992485027_wp, 1.06348337074132352_wp, -0.257894305390896316_wp, &
      1.00391006635335449_wp, -0.0626221498112348254_wp, 1.00000381470090361_wp, -0.00195312872529266694_wp, 1.0_wp, &
      0.0_wp, 1.00000381470090361_wp, 0.00195312872529266694_wp, 1.00391006635335449_wp, 0.0626221498112348254_wp, &
      1.06348337074132352_wp, 0.257894305390896316_wp, 1.26606587775200834_wp, 0.565159103992485027_wp, &
      2.27958530233606727_wp, 1.59063685463732906_wp, 4.88079258586502409_wp, 3.9533702174026094_wp, &
      11.3019219521363305_wp, 9.75946515370444991_wp, 427.564115721804785_wp, 399.873136782560098_wp, &
      893446.227920105017_wp, 865059.435854839471_wp]
   integer,parameter :: which(*)=[ &
      1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2, &
      1,2,1,2,1,2]
   integer,parameter :: orders(*)=[ &
      0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0, &
      0,0,0,0,0,0]
   real(wp) :: actual,expected,relative_error,maximum_error
   integer :: i
   maximum_error=0
   do i=1,size(inputs)
      select case(which(i))
      case(1)
         actual=real(bessel_i0(real(inputs(i))),wp)
      case(2)
         actual=real(bessel_i1(real(inputs(i))),wp)
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
   print '(a)', 'PASS specfunc-fullerton-modified-bessel-i01-reference'
end program
