! Independent MIT consumer; see licenses/gamma-relative-ten-drivers-MIT.txt.
program main
   use iso_fortran_env,only:wp=>real64
   use ieee_arithmetic,only:ieee_is_finite
   use specfunc_fullerton,only:sign_log_gamma
   implicit none
   real(wp),parameter::aa(*)=[ &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp]
   real(wp),parameter::xx(*)=[ &
      -7.5_wp, -6.5_wp, -5.5_wp, &
      -4.5_wp, -3.5_wp, -2.5_wp, &
      -1.5_wp, -0.5_wp, 0.125_wp, &
      0.5_wp, 1.0_wp, 1.5_wp, &
      2.0_wp, 3.0_wp, 4.0_wp, &
      8.0_wp, 16.0_wp, 32.0_wp]
   real(wp),parameter::expected(*)=[ &
      -8.40453737145159754_wp, -6.38963435090933278_wp, -4.51783217400774135_wp, &
      -2.81308408176931612_wp, -1.30900668499304205_wp, -0.0562437164976740507_wp, &
      0.860047015376481015_wp, 1.2655121234846454_wp, 2.01941835755379635_wp, &
      0.572364942924700087_wp, 0.0_wp, -0.120782237635245222_wp, &
      0.0_wp, 0.693147180559945309_wp, 1.791759469228055_wp, &
      8.5251613610654143_wp, 27.8992713838408916_wp, 78.0922235533153106_wp]
   integer,parameter::orders(*)=[ &
      1,-1,1,-1,1,-1,1,-1,1,1,1,1,1,1,1,1,1,1]
   real(wp)::actual,error,maximum_error
   real::logvalue,sgn
   integer::i
   maximum_error=0
   do i=1,size(expected)
      call sign_log_gamma(real(xx(i)),logvalue,sgn)
      actual=real(logvalue,wp)
      if(.not.ieee_is_finite(actual)) error stop 'Nonfinite result'
      error=abs(actual-expected(i))/max(abs(expected(i)),1.e-30_wp)
      if(error>5.e-5_wp) then
         print *, 'Case, a, x, n, actual, reference:',i,aa(i),xx(i),orders(i),actual,expected(i)
         error stop 'Independent high precision reference'
      end if
      maximum_error=max(maximum_error,error)
      if(.not.ieee_is_finite(sgn)) error stop 'Nonfinite gamma sign'
      if(sgn/=real(orders(i))) error stop 'Gamma sign'
   end do
   print '(a,i0)', 'Default REAL32 comparisons with independent high precision references: ',size(expected)
   print '(a,es12.4)', 'Maximum relative error (reference floor 1e-30): ',maximum_error
   print '(a)', 'PASS specfunc-fullerton-signed-log-gamma-reference'
end program
