! Independent MIT consumer; see licenses/gamma-relative-ten-drivers-MIT.txt.
program main
   use iso_fortran_env,only:wp=>real64
   use ieee_arithmetic,only:ieee_is_finite
   use specfunc_fullerton,only:reciprocal_gamma
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
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp]
   real(wp),parameter::xx(*)=[ &
      0.0_wp, -1.0_wp, -2.0_wp, &
      -3.0_wp, -4.0_wp, -5.0_wp, &
      -6.0_wp, -7.0_wp, -8.0_wp, &
      -9.0_wp, -10.0_wp, -11.0_wp, &
      -12.0_wp, -11.5_wp, -10.5_wp, &
      -9.5_wp, -8.5_wp, -7.5_wp, &
      -6.5_wp, -5.5_wp, -4.5_wp, &
      -3.5_wp, -2.5_wp, -1.5_wp, &
      -0.5_wp, 0.5_wp, 1.5_wp, &
      2.5_wp, 3.5_wp, 4.5_wp, &
      5.5_wp, 6.5_wp, 7.5_wp, &
      8.5_wp, 9.5_wp, 10.5_wp, &
      11.5_wp, 12.5_wp, 13.5_wp, &
      14.5_wp, 15.5_wp]
   real(wp),parameter::expected(*)=[ &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 43558596.086351139_wp, -3787704.00750879469_wp, &
      360733.71500083759_wp, -37971.9700000881674_wp, 4467.29058824566675_wp, &
      -595.638745099422233_wp, 91.6367300152957282_wp, -16.6612236391446778_wp, &
      3.70249414203215063_wp, -1.05785546915204304_wp, 0.423142187660817215_wp, &
      -0.282094791773878143_wp, 0.564189583547756287_wp, 1.12837916709551257_wp, &
      0.752252778063675049_wp, 0.30090111122547002_wp, 0.0859717460644200056_wp, &
      0.0191048324587600013_wp, 0.0034736059015927275_wp, 0.000534400907937342692_wp, &
      0.0000712534543916456923_wp, 8.38275934019361086e-6_wp, 8.82395720020380091e-7_wp, &
      8.40376876209885801e-8_wp, 7.30762501052074609e-9_wp, 5.84610000841659687e-10_wp, &
      4.33044445067896065e-11_wp, 2.98651341426135217e-12_wp]
   integer,parameter::orders(*)=[ &
      0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0, &
      0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
   real(wp)::actual,error,maximum_error
   real::logvalue,sgn
   integer::i
   maximum_error=0
   do i=1,size(expected)
      actual=real(reciprocal_gamma(real(xx(i))),wp)
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
   print '(a)', 'PASS specfunc-fullerton-reciprocal-gamma-pole-zeros-reference'
end program
