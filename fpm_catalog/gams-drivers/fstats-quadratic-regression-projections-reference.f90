! Independent MIT consumer; see licenses/fstats-fitting-ten-drivers-MIT.txt.
program main
   use iso_fortran_env,only:wp=>real64
   use ieee_arithmetic,only:ieee_is_finite
   use fstats_linear_regression,only: &
      linear_least_squares
   implicit none
   real(wp),allocatable::x(:),y(:),ymod(:),resid(:)
   real(wp)::coeff(3),a,b,c,eta,s2,s4,s6,det,expected(3),value
   integer::n,i,variant
   do n=5,13,2
      allocate(x(n),y(n),ymod(n),resid(n))
      x=[(real(i-(n+1)/2,wp)/4,i=1,n)]
      s2=sum(x**2);s4=sum(x**4);s6=sum(x**6);det=n*s4-s2*s2
      do variant=1,3
         a=real(variant,wp)/4;b=-0.75_wp;c=0.5_wp;eta=real(variant,wp)/64
         y=a+b*x+c*x*x+eta*x**4
         expected=[a+eta*(s4*s4-s2*s6)/det,b,c+eta*(n*s6-s2*s4)/det]
         call linear_least_squares(2,.true.,x,y,coeff,ymod,resid)
         do i=1,3
            call check(coeff(i),expected(i))
         end do
         do i=1,n
            value=expected(1)+expected(2)*x(i)+expected(3)*x(i)**2
            call check(ymod(i),value);call check(resid(i),value-y(i))
         end do
         call check(sum(resid),0._wp)
         call check(sum(x*resid),0._wp)
         call check(sum(x*x*resid),0._wp)
      end do
      deallocate(x,y,ymod,resid)
   end do
   print '(a)', '15 noisy quadratic projections and normal-equation residuals checked.'
   print '(a)', 'PASS fstats-quadratic-regression-projections-reference'
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
