! Independent MIT consumer; see licenses/grids-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64, int64
   use ieee_arithmetic, only: ieee_is_finite
   use stdlib_math, only: linspace
   implicit none

   real(real64),allocatable :: values(:)
   complex(real64),allocatable :: zvalues(:)
   real(real64) :: a,b,r
   complex(real64) :: za,zb,zr
   integer :: ia,ib,n,i,count
   count=0
   do ia=-4,4
      do ib=-4,4
         a=real(ia,real64)/2; b=real(ib,real64)/2
         za=cmplx(a,b,real64); zb=cmplx(b,-a,real64)
         do n=-2,33
            values=linspace(a,b,n); zvalues=linspace(za,zb,n)
            if(size(values)/=max(0,n).or.size(zvalues)/=max(0,n)) error stop 'Grid length'
            do i=1,n
               if(n==1) then
                  r=b; zr=zb
               else
                  r=(real(n-i,real64)*a+real(i-1,real64)*b)/real(n-1,real64)
                  zr=(real(n-i,real64)*za+real(i-1,real64)*zb)/real(n-1,real64)
               end if
               call check(values(i),r)
               call check(real(zvalues(i),real64),real(zr,real64))
               call check(aimag(zvalues(i)),aimag(zr))
            end do
            count=count+1
         end do
      end do
   end do
   values=linspace(-3._real64,5._real64)
   if(size(values)/=100) error stop 'Default linear-grid length'
   do i=1,100
      call check(values(i),(-3._real64*(100-i)+5._real64*(i-1))/99)
   end do
   print '(a,i0,a)', 'Independent linear grids: ',count,' real and complex; default length: 100'
   print '(a)', 'PASS stdlib-linear-grids-reference'
contains
   subroutine check(actual,expected)
      real(real64),intent(in) :: actual,expected
      if(.not.ieee_is_finite(actual)) error stop 'Nonfinite result'
      if(abs(actual-expected)>3.e-13_real64*max(1._real64,abs(expected))) error stop 'Independent reference'
   end subroutine
end program
