! Independent MIT consumer; see licenses/gamma-relative-ten-drivers-MIT.txt.
program main
   use iso_fortran_env,only:wp=>real64
   use ieee_arithmetic,only:ieee_is_finite
   use specfunc_fullerton,only:inverse_chi
   implicit none
   real(wp),parameter::aa(*)=[ &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp]
   real(wp),parameter::xx(*)=[ &
      -16.0_wp, -8.0_wp, -4.0_wp, &
      -3.0_wp, -2.0_wp, -1.0_wp, &
      -0.5_wp, -0.125_wp, -0.00390625_wp, &
      -1.52587890625e-05_wp, 0.0_wp, 1.52587890625e-05_wp, &
      0.00390625_wp, 0.125_wp, 0.5_wp, &
      1.0_wp, 2.0_wp, 3.0_wp, &
      4.0_wp, 8.0_wp, 16.0_wp]
   real(wp),parameter::expected(*)=[ &
      297777.149531028039_wp, 217.533273728026344_wp, 7.85003753280176208_wp, &
      3.28456414119596721_wp, 1.18230407718543635_wp, 0.26065127607867538_wp, &
      0.0631546707019188329_wp, 0.00390879401472700301_wp, 3.81469969094502712e-6_wp, &
      5.82076609140320959e-11_wp, 0.0_wp, 5.82076609140320959e-11_wp, &
      3.81469969094502712e-6_wp, 0.00390879401472700301_wp, 0.0631546707019188329_wp, &
      0.26065127607867538_wp, 1.18230407718543635_wp, 3.28456414119596721_wp, &
      7.85003753280176208_wp, 217.533273728026344_wp, 297777.149531028039_wp]
   integer,parameter::orders(*)=[ &
      0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
   real(wp)::actual,error,maximum_error
   real::logvalue,sgn
   integer::i
   maximum_error=0
   do i=1,size(expected)
      actual=real(inverse_chi(real(xx(i))),wp)
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
   print '(a)', 'PASS specfunc-fullerton-entire-hyperbolic-integral-reference'
end program
