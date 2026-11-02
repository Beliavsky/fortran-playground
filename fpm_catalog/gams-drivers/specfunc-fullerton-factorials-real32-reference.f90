! Independent MIT consumer; see licenses/gamma-relative-ten-drivers-MIT.txt.
program main
   use iso_fortran_env,only:wp=>real64
   use ieee_arithmetic,only:ieee_is_finite
   use specfunc_fullerton,only:factorial
   implicit none
   real(wp),parameter::aa(*)=[ &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp]
   real(wp),parameter::xx(*)=[ &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp]
   real(wp),parameter::expected(*)=[ &
      1.0_wp, 1.0_wp, 2.0_wp, &
      6.0_wp, 24.0_wp, 120.0_wp, &
      720.0_wp, 5040.0_wp, 40320.0_wp, &
      362880.0_wp, 3628800.0_wp, 39916800.0_wp, &
      479001600.0_wp, 6227020800.0_wp, 87178291200.0_wp, &
      1307674368000.0_wp, 20922789888000.0_wp, 355687428096000.0_wp, &
      6402373705728000.0_wp, 121645100408832000.0_wp, 2.43290200817664e+18_wp, &
      5.109094217170944e+19_wp, 1.12400072777760768e+21_wp, 2.58520167388849766e+22_wp, &
      6.20448401733239439e+23_wp, 1.5511210043330986e+25_wp, 4.03291461126605636e+26_wp, &
      1.08888694504183522e+28_wp, 3.04888344611713861e+29_wp, 8.84176199373970195e+30_wp, &
      2.65252859812191059e+32_wp, 8.22283865417792282e+33_wp, 2.6313083693369353e+35_wp, &
      8.6833176188118865e+36_wp]
   integer,parameter::orders(*)=[ &
      0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24, &
      25,26,27,28,29,30,31,32,33]
   real(wp)::actual,error,maximum_error
   real::logvalue,sgn
   integer::i
   maximum_error=0
   do i=1,size(expected)
      actual=real(factorial(orders(i)),wp)
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
   print '(a)', 'PASS specfunc-fullerton-factorials-real32-reference'
end program
