! Independent MIT consumer; see licenses/grids-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64, int64
   use ieee_arithmetic, only: ieee_is_finite
   use stdlib_math, only: deg2rad, rad2deg
   implicit none
   real(real64),parameter :: pi=3.1415926535897932384626433832795029_real64

   real(real64) :: degrees(145),radians(145),actual(145)
   integer :: i
   degrees=[(real(15*i,real64),i=-72,72)]
   radians=[(pi*real(i,real64)/12,i=-72,72)]
   actual=deg2rad(degrees)
   do i=1,145
      call check(actual(i),radians(i))
   end do
   actual=rad2deg(radians)
   do i=1,145
      call check(actual(i),degrees(i))
      call check(rad2deg(deg2rad(degrees(i))),degrees(i))
   end do
   print '(a)', 'Independent degree/radian conversions: 145 angles in each direction'
   print '(a)', 'PASS stdlib-angle-units-reference'
contains
   subroutine check(actual,expected)
      real(real64),intent(in) :: actual,expected
      if(.not.ieee_is_finite(actual)) error stop 'Nonfinite result'
      if(abs(actual-expected)>3.e-13_real64*max(1._real64,abs(expected))) error stop 'Independent reference'
   end subroutine
end program
