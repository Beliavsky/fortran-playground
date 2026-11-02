! Independent MIT consumer; see licenses/grids-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64, int64
   use ieee_arithmetic, only: ieee_is_finite
   use stdlib_math, only: clip
   implicit none

   real(real64) :: x(129),y(129),lo,hi,expected
   integer :: i,l,h,count
   integer(int64) :: ix(5),iy(5)
   x=[(real(i-65,real64)/8,i=1,129)]; count=0
   do l=-2,2
      do h=l,2
         lo=real(l,real64); hi=real(h,real64); y=clip(x,lo,hi)
         do i=1,129
            expected=x(i)
            if(x(i)<lo) expected=lo
            if(x(i)>hi) expected=hi
            call check(y(i),expected)
            call check(clip(x(i),lo,hi),expected)
            count=count+1
         end do
      end do
   end do
   ix=[-3000000000000_int64,-1000000000000_int64,0_int64,1000000000000_int64,3000000000000_int64]
   iy=clip(ix,-1000000000000_int64,1000000000000_int64)
   if(any(iy/=[-1000000000000_int64,-1000000000000_int64,0_int64,1000000000000_int64,1000000000000_int64])) &
      error stop 'Large integer clipping reference'
   if(any(x/=[(real(i-65,real64)/8,i=1,129)])) error stop 'Clipping input preservation'
   print '(a,i0,a)', 'Independent clipping references: ',count,'; large integers: 5'
   print '(a)', 'PASS stdlib-bounded-clipping-reference'
contains
   subroutine check(actual,expected)
      real(real64),intent(in) :: actual,expected
      if(.not.ieee_is_finite(actual)) error stop 'Nonfinite result'
      if(abs(actual-expected)>3.e-13_real64*max(1._real64,abs(expected))) error stop 'Independent reference'
   end subroutine
end program
