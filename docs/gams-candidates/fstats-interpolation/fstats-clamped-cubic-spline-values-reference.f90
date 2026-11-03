! Independent MIT consumer; see licenses/fstats-fitting-ten-drivers-MIT.txt.
program main
   use iso_fortran_env,only:wp=>real64
   use ieee_arithmetic,only:ieee_is_finite
   use fstats_interp,only: &
      spline_interpolator,SPLINE_KNOWN_FIRST_DERIVATIVE
   implicit none
   type(spline_interpolator)::fit
   real(wp),parameter::x(5)=[-2._wp,-0.75_wp,0._wp,0.5_wp,2._wp]
   real(wp)::y(5),q(41),values(41),expected,t,u
   integer::variant,i,j,k
   real(wp)::a,b,c,d,left_slope,right_slope
   do variant=1,3
      a=real(variant,wp)/8;b=-0.5_wp;c=0.75_wp;d=real(2-variant,wp)
      y=((a*x+b)*x+c)*x+d
      left_slope=(3*a*x(1)+2*b)*x(1)+c
      right_slope=(3*a*x(5)+2*b)*x(5)+c
      call fit%initialize(x,y,SPLINE_KNOWN_FIRST_DERIVATIVE,left_slope, &
         SPLINE_KNOWN_FIRST_DERIVATIVE,right_slope)
      q(1:33)=[(-2._wp+real(i-1,wp)/8,i=1,33)]
      call fit%interpolate(q(1:33),values(1:33))
      do i=1,33
         expected=((a*q(i)+b)*q(i)+c)*q(i)+d
         call check(values(i),expected)
         call check(fit%interpolate_value(q(i)),expected)
      end do
   end do
   print '(a)', '99 clamped cubic spline queries independently checked.'
   print '(a)', 'PASS fstats-clamped-cubic-spline-values-reference'
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
