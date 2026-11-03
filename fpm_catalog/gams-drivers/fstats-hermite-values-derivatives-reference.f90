! Independent MIT consumer; see licenses/fstats-fitting-ten-drivers-MIT.txt.
program main
   use iso_fortran_env,only:wp=>real64
   use ieee_arithmetic,only:ieee_is_finite
   use fstats_interp,only: &
      hermite_interpolator
   implicit none
   type(hermite_interpolator),allocatable::fit
   real(wp),parameter::x(3)=[-1._wp,-0.25_wp,1._wp]
   real(wp)::y(3),yp(3),q(33),values(33),derivs(33),coeff(0:5),expected,expected_deriv
   integer::degree,i,j
   do degree=1,5
      allocate(fit)
      coeff=0
      do j=0,degree
         coeff(j)=real((-1)**j*(j+1),wp)/16
      end do
      do i=1,3
         y(i)=sum([(coeff(j)*x(i)**j,j=0,degree)])
         yp(i)=sum([(j*coeff(j)*x(i)**(j-1),j=1,degree)])
      end do
      call fit%initialize(x,y,yp)
      q=[(-1._wp+real(i-1,wp)/16,i=1,33)]
      call fit%interpolate_with_derivative(q,values,derivs)
      do i=1,33
         expected=sum([(coeff(j)*q(i)**j,j=0,degree)])
         expected_deriv=sum([(j*coeff(j)*q(i)**(j-1),j=1,degree)])
         call check(values(i),expected)
         call check(derivs(i),expected_deriv)
         call check(fit%interpolate_value(q(i)),expected)
      end do
      deallocate(fit)
   end do
   print '(a)', '165 global Hermite values and first derivatives independently checked.'
   print '(a)', 'PASS fstats-hermite-values-derivatives-reference'
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
