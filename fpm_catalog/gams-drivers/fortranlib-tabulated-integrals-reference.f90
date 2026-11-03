! Independent MIT consumer; see licenses/next-numerical-drivers-MIT.txt.
program main
   use iso_fortran_env,only:wp=>real64
   use ieee_arithmetic,only:ieee_is_finite
   use lib_array,only:integral
   implicit none
   real(wp),parameter::x(5)=[-2._wp,-0.75_wp,0._wp,0.5_wp,2._wp]
   real(wp)::y(5),q,expected,t,left,right,slope,intercept,lo,hi
   integer::variant,i,j,k,cases
   real(wp),parameter::limits(*)=[-3._wp,-2._wp,-1.875_wp,-0.75_wp,-0.25_wp, &
      0._wp,0.25_wp,0.5_wp,1.5_wp,2._wp,3._wp]
   real(wp)::value
   integer::a,b
   cases=0
   do variant=1,3
      y=[(real(modulo(i*i+variant*i,11)-5,wp)/4,i=1,5)]
      do a=1,size(limits)
         do b=a,size(limits)
            lo=max(limits(a),x(1));hi=min(limits(b),x(5));expected=0
            do j=1,4
               left=max(lo,x(j));right=min(hi,x(j+1))
               if(right<=left) cycle
               slope=(y(j+1)-y(j))/(x(j+1)-x(j));intercept=y(j)-slope*x(j)
               expected=expected+intercept*(right-left)+slope*(right**2-left**2)/2
            end do
            value=integral(x,y,limits(a),limits(b));call check(value,expected)
            cases=cases+1
         end do
      end do
      expected=sum([( (x(j+1)-x(j))*(y(j+1)+y(j))/2,j=1,4)])
      call check(integral(x,y),expected)
   end do
   print '(a,i0)', 'Clipped piecewise-linear area intervals plus three full integrals: ',cases
   print '(a)', 'PASS fortranlib-tabulated-integrals-reference'
contains
   subroutine check(actual,expected)
      real(wp),intent(in)::actual,expected
      if(.not.ieee_is_finite(actual)) error stop 'Nonfinite result'
      if(abs(actual-expected)>2.e-12_wp*max(abs(expected),1._wp)) then
         print *, 'Actual, expected:',actual,expected
         error stop 'Independent reference'
      end if
   end subroutine
end program
