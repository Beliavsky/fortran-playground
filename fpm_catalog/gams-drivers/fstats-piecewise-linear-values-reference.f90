! Independent MIT consumer; see licenses/fstats-fitting-ten-drivers-MIT.txt.
program main
   use iso_fortran_env,only:wp=>real64
   use ieee_arithmetic,only:ieee_is_finite
   use fstats_interp,only: &
      linear_interpolator
   implicit none
   type(linear_interpolator)::fit
   real(wp),parameter::x(5)=[-2._wp,-0.75_wp,0._wp,0.5_wp,2._wp]
   real(wp)::y(5),q(41),values(41),expected,t,u
   integer::variant,i,j,k
   do variant=1,3
      y=[(real(modulo(i*i+variant*i,11)-5,wp)/4,i=1,5)]
      call fit%initialize(x,y)
      q=[(-2.5_wp+real(i-1,wp)/8,i=1,41)]
      call fit%interpolate(q,values)
      do i=1,size(q)
         j=1
         do k=2,4
            if(q(i)>=x(k)) j=k
         end do
         t=(q(i)-x(j))/(x(j+1)-x(j))
         expected=(1-t)*y(j)+t*y(j+1)
         call check(values(i),expected)
         call check(fit%interpolate_value(q(i)),expected)
      end do
      do i=1,5
         call check(fit%interpolate_value(x(i)),y(i))
      end do
   end do
   print '(a)', '123 irregular-grid piecewise-linear queries and 15 nodes checked.'
   print '(a)', 'PASS fstats-piecewise-linear-values-reference'
contains
   subroutine check(actual,expected)
      real(wp),intent(in)::actual,expected
      if(.not.ieee_is_finite(actual)) error stop 'Nonfinite result'
      if(abs(actual-expected)>2.e-10_wp*max(1._wp,abs(expected))) then
         print *, 'Actual, expected:',actual,expected
         error stop 'Independent reference'
      end if
   end subroutine
   subroutine probability_check(actual,expected)
      real(wp),intent(in)::actual,expected
      if(.not.ieee_is_finite(actual)) error stop 'Nonfinite probability'
      if(abs(actual-expected)>2.e-9_wp*max(1.e-30_wp,abs(expected))) then
         print *, 'Actual probability, expected:',actual,expected
         error stop 'Independent probability reference'
      end if
   end subroutine
   subroutine insertion_sort(x)
      real(wp),intent(inout)::x(:)
      real(wp)::value
      integer::i,j
      do i=2,size(x)
         value=x(i);j=i-1
         do while(j>=1)
            if(x(j)<=value) exit
            x(j+1)=x(j);j=j-1
         end do
         x(j+1)=value
      end do
   end subroutine
   function local_median(sorted) result(value)
      real(wp),intent(in)::sorted(:)
      real(wp)::value
      integer::n
      n=size(sorted);value=(sorted((n+1)/2)+sorted(n/2+1))/2
   end function
end program
