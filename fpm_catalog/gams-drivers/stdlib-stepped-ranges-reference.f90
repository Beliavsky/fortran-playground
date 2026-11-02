! Independent MIT consumer; see licenses/grids-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64, int64
   use ieee_arithmetic, only: ieee_is_finite
   use stdlib_math, only: arange
   implicit none

   real(real64),allocatable :: values(:)
   integer(int64),allocatable :: ivals(:)
   real(real64),parameter :: steps(3)=[0.25_real64,0.5_real64,1._real64]
   real(real64) :: a,b,step,current,expected(40)
   integer :: ia,ib,k,n,i,count,idir
   count=0
   do ia=-8,8
      do ib=-8,8
         a=real(ia,real64)/4; b=real(ib,real64)/4
         do k=1,3
            step=steps(k)
            if(b<a) step=-step
            n=0; current=a
            do
               if(step>0.and.current>b) exit
               if(step<0.and.current<b) exit
               n=n+1; expected(n)=current; current=current+step
            end do
            values=arange(a,b,steps(k))
            if(size(values)/=n) error stop 'Inclusive stepped-range length'
            do i=1,n
               call check(values(i),expected(i))
            end do
            count=count+1
         end do
      end do
   end do
   do ia=-8,8
      ivals=arange(int(ia,int64)); idir=1
      if(ia<1) idir=-1
      if(size(ivals)/=abs(ia-1)+1) error stop 'Single-argument integer range'
      do i=1,size(ivals)
         if(ivals(i)/=1+(i-1)*idir) error stop 'Integer repeated-step reference'
      end do
   end do
   print '(a,i0,a)', 'Independent dyadic stepped ranges: ',count,'; INT64 ranges: 17'
   print '(a)', 'PASS stdlib-stepped-ranges-reference'
contains
   subroutine check(actual,expected)
      real(real64),intent(in) :: actual,expected
      if(.not.ieee_is_finite(actual)) error stop 'Nonfinite result'
      if(abs(actual-expected)>3.e-13_real64*max(1._real64,abs(expected))) error stop 'Independent reference'
   end subroutine
end program
