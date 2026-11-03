! Independent MIT consumer; see licenses/next-numerical-drivers-MIT.txt.
program main
   use iso_fortran_env,only:real64
   use assert,only:wp
   use funcs,only:besi0
   use ieee_arithmetic,only:ieee_is_finite
   implicit none
   real(wp),parameter::x(*)=[ &
      0.0_wp, -9.313225746154785e-10_wp, 9.313225746154785e-10_wp, &
      -3.0517578125e-05_wp, 3.0517578125e-05_wp, -0.125_wp, &
      0.125_wp, -0.5_wp, 0.5_wp, &
      -1.0_wp, 1.0_wp, -2.0_wp, &
      2.0_wp, -4.0_wp, 4.0_wp, &
      -8.0_wp, 8.0_wp, -14.9990234375_wp, &
      14.9990234375_wp, -15.0_wp, 15.0_wp, &
      -15.0009765625_wp, 15.0009765625_wp, -16.0_wp, &
      16.0_wp, -32.0_wp, 32.0_wp, &
      -64.0_wp, 64.0_wp]
   real(wp),parameter::expected(*)=[ &
      1.0_wp, 1.0_wp, 1.0_wp, &
      1.00000000023283064_wp, 1.00000000023283064_wp, 1.00391006635335449_wp, &
      1.00391006635335449_wp, 1.06348337074132352_wp, 1.06348337074132352_wp, &
      1.26606587775200834_wp, 1.26606587775200834_wp, 2.27958530233606727_wp, &
      2.27958530233606727_wp, 11.3019219521363305_wp, 11.3019219521363305_wp, &
      427.564115721804785_wp, 427.564115721804785_wp, 339329.090282575588_wp, &
      339329.090282575588_wp, 339649.37329791388_wp, 339649.37329791388_wp, &
      339969.959366538084_wp, 339969.959366538084_wp, 893446.227920105017_wp, &
      893446.227920105017_wp, 5590908381350.87309_wp, 5590908381350.87309_wp, &
      3.11545791818789756e+26_wp, 3.11545791818789756e+26_wp]
   real(wp)::value
   integer::i
   if(wp/=real64) error stop 'Expected real64 besi0'
   do i=1,size(x)
      value=besi0(x(i))
      call check(value,expected(i))
      if(value<=0) error stop 'Positive I0'
      call check(besi0(-x(i)),expected(i))
   end do
   print '(a,i0)', 'Independent high precision reference points: ',size(x)
   print '(a)', 'PASS rpn-bessel-i0-values-reference'
contains
   subroutine check(actual,expected)
      real(wp),intent(in)::actual,expected
      if(.not.ieee_is_finite(actual)) error stop 'Nonfinite result'
      if(abs(actual-expected)>2.e-12_wp*max(abs(expected),1.e-100_wp)) then
         print *, 'Actual, expected:',actual,expected
         error stop 'Independent reference'
      end if
   end subroutine
end program
