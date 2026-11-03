! Independent MIT consumer; see licenses/fstats-fitting-ten-drivers-MIT.txt.
program main
   use iso_fortran_env,only:wp=>real64
   use ieee_arithmetic,only:ieee_is_finite
   use fstats_linear_regression,only: &
      linear_least_squares
   implicit none
   real(wp),allocatable::x(:),y(:),ymod(:),resid(:)
   real(wp)::coeff(2),a,b,xb,yb,expected
   integer::n,i,variant,mode
   logical::intercept
   do n=3,25
      allocate(x(n),y(n),ymod(n),resid(n))
      x=[(real(i,wp)/4-2,i=1,n)]
      do variant=1,3
         y=[(1.5_wp-real(variant,wp)*x(i)/4+real(modulo(7*i,5)-2,wp)/16,i=1,n)]
         do mode=0,1
            intercept=mode==1
            if(intercept) then
               xb=sum(x)/n;yb=sum(y)/n
               b=sum((x-xb)*(y-yb))/sum((x-xb)**2);a=yb-b*xb
            else
               a=0;b=sum(x*y)/sum(x*x)
            end if
            call linear_least_squares(1,intercept,x,y,coeff,ymod,resid)
            call check(coeff(1),a);call check(coeff(2),b)
            do i=1,n
               expected=a+b*x(i)
               call check(ymod(i),expected);call check(resid(i),expected-y(i))
            end do
            call check(sum(x*resid),0._wp)
            if(intercept) call check(sum(resid),0._wp)
         end do
      end do
      deallocate(x,y,ymod,resid)
   end do
   print '(a)', '138 noisy linear fits, coefficients, residuals and orthogonality checked.'
   print '(a)', 'PASS fstats-linear-regression-residuals-reference'
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
