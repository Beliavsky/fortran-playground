! Independent MIT consumer; see licenses/fstats-fitting-ten-drivers-MIT.txt.
program main
   use iso_fortran_env,only:wp=>real64
   use ieee_arithmetic,only:ieee_is_finite
   use fstats_interp,only: &
      polynomial_interpolator
   implicit none
   type(polynomial_interpolator)::fit
   real(wp),parameter::x(5)=[-2._wp,-0.75_wp,0._wp,0.5_wp,2._wp]
   real(wp)::y(5),q(41),values(41),expected,t,u
   integer::variant,i,j,k
   integer::degree
   real(wp)::coeff(0:4)
   do degree=1,4
      coeff=0
      do j=0,degree
         coeff(j)=real((-1)**j*(j+1),wp)/8
      end do
      do i=1,5
         y(i)=sum([(coeff(j)*x(i)**j,j=0,degree)])
      end do
      call fit%initialize(degree,x,y)
      q=[(-2.5_wp+real(i-1,wp)/8,i=1,41)]
      call fit%interpolate(q,values)
      do i=1,size(q)
         expected=sum([(coeff(j)*q(i)**j,j=0,degree)])
         call check(values(i),expected)
         call check(fit%interpolate_value(q(i)),expected)
      end do
   end do
   print '(a)', '164 polynomial queries, degrees 1 through 4, checked.'
   print '(a)', 'PASS fstats-polynomial-interpolation-values-reference'
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
