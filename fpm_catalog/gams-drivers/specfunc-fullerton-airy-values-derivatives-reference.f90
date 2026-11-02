! Independent MIT consumer; see licenses/fullerton-functions-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: wp=>real64
   use ieee_arithmetic, only: ieee_is_finite
   use specfunc_fullerton, only: &
      airy_ai, airy_bi, airy_aiprime, airy_biprime
   implicit none
   real(wp),parameter :: inputs(*)=[ &
      -8.0_wp, -8.0_wp, -8.0_wp, -8.0_wp, -4.0_wp, -4.0_wp, -4.0_wp, -4.0_wp, -2.0_wp, -2.0_wp, -2.0_wp, -2.0_wp, &
      -1.0_wp, -1.0_wp, -1.0_wp, -1.0_wp, -0.5_wp, -0.5_wp, -0.5_wp, -0.5_wp, -0.125_wp, -0.125_wp, -0.125_wp, &
      -0.125_wp, 0.0_wp, 0.0_wp, 0.0_wp, 0.0_wp, 0.125_wp, 0.125_wp, 0.125_wp, 0.125_wp, 0.5_wp, 0.5_wp, 0.5_wp, &
      0.5_wp, 1.0_wp, 1.0_wp, 1.0_wp, 1.0_wp, 2.0_wp, 2.0_wp, 2.0_wp, 2.0_wp, 3.0_wp, 3.0_wp, 3.0_wp, 3.0_wp, &
      4.0_wp, 4.0_wp, 4.0_wp, 4.0_wp, 8.0_wp, 8.0_wp, 8.0_wp, 8.0_wp]
   real(wp),parameter :: references(*)=[ &
      -0.0527050503563862026_wp, -0.33125158075113786_wp, 0.935560938198306551_wp, -0.159450497812981389_wp, &
      -0.0702655329492895151_wp, 0.39223470570699929_wp, -0.79062857536858138_wp, -0.116670567438340894_wp, &
      0.227407428201685576_wp, -0.412302587956398488_wp, 0.618259020741691041_wp, 0.278795166921169523_wp, &
      0.535560883292352119_wp, 0.103997389496944612_wp, -0.0101605671166452094_wp, 0.592375626422792351_wp, &
      0.475728091610539589_wp, 0.38035265975105385_wp, -0.204081670339547386_wp, 0.505933713623847167_wp, &
      0.387259652408395772_wp, 0.558699544406067727_wp, -0.25587761975663491_wp, 0.45280001547160431_wp, &
      0.355028053887817239_wp, 0.614926627446000735_wp, -0.258819403792806798_wp, 0.448288357353826358_wp, &
      0.322785939026777916_wp, 0.671171977449897641_wp, -0.25621390188308172_wp, 0.453384975343142057_wp, &
      0.23169360648083349_wp, 0.854277043103155493_wp, -0.224910532664683893_wp, 0.544572564140592302_wp, &
      0.135292416312881416_wp, 1.20742359495287126_wp, -0.159147441296793213_wp, 0.932435933392775633_wp, &
      0.0349241304232743791_wp, 3.29809499997821471_wp, -0.0530903844336536317_wp, 4.10068204993288989_wp, &
      0.00659113935746071914_wp, 14.037328963730232_wp, -0.0119129767059513185_wp, 22.9222149663821702_wp, &
      0.000951563851204801874_wp, 83.8470714084681399_wp, -0.0019586409502041789_wp, 161.926683504613402_wp, &
      4.69220761609923163e-8_wp, 1199586.00412445993_wp, -1.34143929790678657e-7_wp, 3354342.31274453888_wp]
   integer,parameter :: which(*)=[ &
      1,2,3,4,1,2,3,4,1,2,3,4,1,2,3,4,1,2,3,4,1,2,3,4,1,2,3,4,1,2, &
      3,4,1,2,3,4,1,2,3,4,1,2,3,4,1,2,3,4,1,2,3,4,1,2,3,4]
   integer,parameter :: orders(*)=[ &
      0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0, &
      0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
   real(wp) :: actual,expected,relative_error,maximum_error
   integer :: i
   maximum_error=0
   do i=1,size(inputs)
      select case(which(i))
      case(1)
         actual=real(airy_ai(real(inputs(i))),wp)
      case(2)
         actual=real(airy_bi(real(inputs(i))),wp)
      case(3)
         actual=real(airy_aiprime(real(inputs(i))),wp)
      case(4)
         actual=real(airy_biprime(real(inputs(i))),wp)
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
   print '(a)', 'PASS specfunc-fullerton-airy-values-derivatives-reference'
end program
