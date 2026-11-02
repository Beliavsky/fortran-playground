! Independent MIT consumer; see licenses/gamma-relative-ten-drivers-MIT.txt.
program main
   use iso_fortran_env,only:wp=>real64
   use ieee_arithmetic,only:ieee_is_finite
   use specfunc_fullerton,only:poch
   implicit none
   real(wp),parameter::aa(*)=[ &
      0.5_wp, 0.5_wp, 0.5_wp, &
      0.5_wp, 0.5_wp, 0.5_wp, &
      0.5_wp, 0.5_wp, 1.0_wp, &
      1.0_wp, 1.0_wp, 1.0_wp, &
      1.0_wp, 1.0_wp, 1.0_wp, &
      1.0_wp, 1.5_wp, 1.5_wp, &
      1.5_wp, 1.5_wp, 1.5_wp, &
      1.5_wp, 1.5_wp, 1.5_wp, &
      2.0_wp, 2.0_wp, 2.0_wp, &
      2.0_wp, 2.0_wp, 2.0_wp, &
      2.0_wp, 2.0_wp, 4.0_wp, &
      4.0_wp, 4.0_wp, 4.0_wp, &
      4.0_wp, 4.0_wp, 4.0_wp, &
      4.0_wp, 8.0_wp, 8.0_wp, &
      8.0_wp, 8.0_wp, 8.0_wp, &
      8.0_wp, 8.0_wp, 8.0_wp]
   real(wp),parameter::xx(*)=[ &
      -0.25_wp, 0.0_wp, 0.125_wp, &
      0.5_wp, 1.0_wp, 2.0_wp, &
      3.0_wp, 5.0_wp, -0.25_wp, &
      0.0_wp, 0.125_wp, 0.5_wp, &
      1.0_wp, 2.0_wp, 3.0_wp, &
      5.0_wp, -0.25_wp, 0.0_wp, &
      0.125_wp, 0.5_wp, 1.0_wp, &
      2.0_wp, 3.0_wp, 5.0_wp, &
      -0.25_wp, 0.0_wp, 0.125_wp, &
      0.5_wp, 1.0_wp, 2.0_wp, &
      3.0_wp, 5.0_wp, -0.25_wp, &
      0.0_wp, 0.125_wp, 0.5_wp, &
      1.0_wp, 2.0_wp, 3.0_wp, &
      5.0_wp, -0.25_wp, 0.0_wp, &
      0.125_wp, 0.5_wp, 1.0_wp, &
      2.0_wp, 3.0_wp, 5.0_wp]
   real(wp),parameter::expected(*)=[ &
      2.04553134422633734_wp, 1.0_wp, 0.809340591495618291_wp, &
      0.564189583547756287_wp, 0.5_wp, 0.75_wp, &
      1.875_wp, 29.53125_wp, 1.22541670246517765_wp, &
      1.0_wp, 0.941742699849701488_wp, 0.886226925452758014_wp, &
      1.0_wp, 2.0_wp, 6.0_wp, &
      120.0_wp, 1.02276567211316867_wp, 1.0_wp, &
      1.01167573936952286_wp, 1.12837916709551257_wp, 1.5_wp, &
      3.75_wp, 13.125_wp, 324.84375_wp, &
      0.919062526848883234_wp, 1.0_wp, 1.05946053733091417_wp, &
      1.32934038817913702_wp, 2.0_wp, 6.0_wp, &
      24.0_wp, 720.0_wp, 0.737164735076708427_wp, &
      1.0_wp, 1.17258002178551699_wp, 1.93862139942790815_wp, &
      4.0_wp, 20.0_wp, 120.0_wp, &
      6720.0_wp, 0.606710847458850637_wp, 1.0_wp, &
      1.28786988733082273_wp, 2.78460462172289933_wp, 8.0_wp, &
      72.0_wp, 720.0_wp, 95040.0_wp]
   integer,parameter::orders(*)=[ &
      0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0, &
      0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
   real(wp)::actual,error,maximum_error
   real::logvalue,sgn
   integer::i
   maximum_error=0
   do i=1,size(expected)
      actual=real(poch(real(aa(i)),real(xx(i))),wp)
      if(.not.ieee_is_finite(actual)) error stop 'Nonfinite result'
      error=abs(actual-expected(i))/max(abs(expected(i)),1.e-30_wp)
      if(error>5.e-5_wp) then
         print *, 'Case, a, x, n, actual, reference:',i,aa(i),xx(i),orders(i),actual,expected(i)
         error stop 'Independent high precision reference'
      end if
      maximum_error=max(maximum_error,error)
   end do
   print '(a,i0)', 'Default REAL32 comparisons with independent high precision references: ',size(expected)
   print '(a,es12.4)', 'Maximum relative error (reference floor 1e-30): ',maximum_error
   print '(a)', 'PASS specfunc-fullerton-pochhammer-ratios-reference'
end program
