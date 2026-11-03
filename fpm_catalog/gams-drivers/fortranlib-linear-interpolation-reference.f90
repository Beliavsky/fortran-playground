! Independent MIT consumer; see licenses/next-numerical-drivers-MIT.txt.
program main
   use iso_fortran_env,only:wp=>real64
   use ieee_arithmetic,only:ieee_is_finite
   use lib_array,only:interp1d
   implicit none
   real(wp),parameter::x(5)=[-2._wp,-0.75_wp,0._wp,0.5_wp,2._wp]
   real(wp)::y(5),q,expected,t,left,right,slope,intercept,lo,hi
   integer::variant,i,j,k,cases
   real(wp)::queries(69),values(69)
   real(wp),parameter::fill=-123._wp
   cases=0
   queries(:65)=[(-2._wp+real(i-1,wp)/16,i=1,65)]
   queries(66:)=[-3._wp,-2.25_wp,2.25_wp,3._wp]
   do variant=1,3
      y=[(real(modulo(i*i+variant*i,11)-5,wp)/4,i=1,5)]
      values=interp1d(x,y,queries,bounds_error=.false.,fill_value=fill)
      do i=1,size(queries)
         q=queries(i)
         if(q<x(1).or.q>x(5)) then
            expected=fill
         else
            j=1
            do k=2,4
               if(q>=x(k)) j=k
            end do
            t=(q-x(j))/(x(j+1)-x(j));expected=(1-t)*y(j)+t*y(j+1)
         end if
         call check(values(i),expected)
         call check(interp1d(x,y,q,bounds_error=.false.,fill_value=fill),expected)
         cases=cases+1
      end do
   end do
   print '(a,i0)', 'Irregular-grid scalar/vector queries including fill values: ',cases
   print '(a)', 'PASS fortranlib-linear-interpolation-reference'
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
