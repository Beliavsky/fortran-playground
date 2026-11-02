! Independent MIT consumer; see licenses/fullerton-functions-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: wp=>real64
   use ieee_arithmetic, only: ieee_is_finite
   use specfunc_fullerton, only: &
      bessel_k0, bessel_k1
   implicit none
   real(wp),parameter :: inputs(*)=[ &
      0.00390625_wp, 0.00390625_wp, 0.125_wp, 0.125_wp, 0.5_wp, 0.5_wp, 1.0_wp, 1.0_wp, 2.0_wp, 2.0_wp, 3.0_wp, &
      3.0_wp, 4.0_wp, 4.0_wp, 8.0_wp, 8.0_wp, 16.0_wp, 16.0_wp]
   real(wp),parameter :: references(*)=[ &
      5.66113437027816317_wp, 255.987966558316326_wp, 2.20786908674497006_wp, 7.83111829911575116_wp, &
      0.924419071227665862_wp, 1.65644112000330089_wp, 0.421024438240708333_wp, 0.601907230197234575_wp, &
      0.113893872749533436_wp, 0.139865881816522427_wp, 0.0347395043862792481_wp, 0.0401564311281941844_wp, &
      0.0111596760858530243_wp, 0.0124834988872684315_wp, 0.000146470705222815387_wp, 0.000155369211805001134_wp, &
      3.49941166393649894e-8_wp, 3.60715711752877969e-8_wp]
   integer,parameter :: which(*)=[ &
      1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2]
   integer,parameter :: orders(*)=[ &
      0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
   real(wp) :: actual,expected,relative_error,maximum_error
   integer :: i
   maximum_error=0
   do i=1,size(inputs)
      select case(which(i))
      case(1)
         actual=real(bessel_k0(real(inputs(i))),wp)
      case(2)
         actual=real(bessel_k1(real(inputs(i))),wp)
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
   print '(a)', 'PASS specfunc-fullerton-modified-bessel-k01-reference'
end program
