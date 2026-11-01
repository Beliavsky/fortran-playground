! Independent MIT consumer; see licenses/statistics-services-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64
   use ieee_arithmetic, only: ieee_is_finite,ieee_is_nan
   use stdlib_stats, only: median
   implicit none
   real(real64),allocatable :: x(:),original(:)
   real(real64) :: expected,actual
   integer :: n,t,i,k,j,histogram(-4:4),ordered(64)
   do n=1,64
      allocate(x(n),original(n))
      do t=1,12
         histogram=0
         do i=1,n
            k=mod(7*i+3*t+i*t,9)-4
            x(i)=real(k,real64)/4
            histogram(k)=histogram(k)+1
         end do
         j=0
         do k=-4,4
            do i=1,histogram(k)
               j=j+1
               ordered(j)=k
            end do
         end do
         expected=real(ordered((n+1)/2)+ordered(n/2+1),real64)/8
         original=x
         actual=median(x)
         if(.not.ieee_is_finite(actual).or.actual/=expected) error stop 'Histogram median oracle'
         if(any(x/=original)) error stop 'Input changed'
      end do
      deallocate(x,original)
   end do
   allocate(x(0))
   if(.not.ieee_is_nan(median(x))) error stop 'Empty median status'
   print '(a)', '768 finite medians from independent histograms; odd/even lengths, ties, negative values; empty NaN'
   print '(a)', 'PASS stdlib-median-reference'
end program
