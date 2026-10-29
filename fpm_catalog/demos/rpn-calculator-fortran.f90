program main
   use assert, only: wp
   use funcs, only: cuberoot, sinc, sech, beta, besi0, gcd, lcm
   implicit none
   call check('cube root of -27', cuberoot(-27.0_wp), -3.0_wp)
   call check('sinc(0)', sinc(0.0_wp), 1.0_wp)
   call check('sech(0)', sech(0.0_wp), 1.0_wp)
   call check('beta(2,3)', beta(2.0_wp, 3.0_wp), 1.0_wp/12.0_wp)
   call check('modified Bessel I0(0)', besi0(0.0_wp), 1.0_wp)
   if (gcd(84, 30) /= 6) error stop 'gcd'
   if (lcm(12, 18) /= 36) error stop 'lcm'
   print *, 'gcd(84,30) = 6; lcm(12,18) = 36'
   print *, 'PASS rpn-calculator-fortran'
contains
   subroutine check(label, actual, expected)
      character(*), intent(in) :: label
      real(wp), intent(in) :: actual, expected
      if (abs(actual-expected) > 1.0e-10_wp) then
         print *, label, actual, expected
         error stop 'numerical check'
      end if
      print '(a,": ",f16.10)', label, actual
   end subroutine
end program
