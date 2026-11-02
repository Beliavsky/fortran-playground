! Independent MIT consumer; see licenses/grids-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64, int64
   use ieee_arithmetic, only: ieee_is_finite
   use stdlib_math, only: arg, argd, argpi
   implicit none
   real(real64),parameter :: pi=3.1415926535897932384626433832795029_real64

   integer,parameter :: re(8)=[1,1,0,-1,-1,-1,0,1],im(8)=[0,1,1,1,0,-1,-1,-1]
   real(real64),parameter :: turns(8)=[0._real64,0.25_real64,0.5_real64,0.75_real64, &
      1._real64,-0.75_real64,-0.5_real64,-0.25_real64]
   complex(real64) :: z(8),saved(8)
   real(real64) :: r(8),d(8),p(8)
   integer :: k,i
   do k=-12,12
      z=cmplx(real(re,real64),real(im,real64),real64)*2._real64**k; saved=z
      r=arg(z); d=argd(z); p=argpi(z)
      do i=1,8
         call check(r(i),turns(i)*pi)
         call check(d(i),turns(i)*180)
         call check(p(i),turns(i))
      end do
      if(any(z/=saved)) error stop 'Phase input preservation'
   end do
   print '(a)', 'Independent quadrant phase references: 600 (radians, degrees, pi units)'
   print '(a)', 'PASS stdlib-complex-phase-reference'
contains
   subroutine check(actual,expected)
      real(real64),intent(in) :: actual,expected
      if(.not.ieee_is_finite(actual)) error stop 'Nonfinite result'
      if(abs(actual-expected)>3.e-13_real64*max(1._real64,abs(expected))) error stop 'Independent reference'
   end subroutine
end program
