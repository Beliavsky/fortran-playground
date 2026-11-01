! Independent MIT consumer; see licenses/distribution-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64
   use ieee_arithmetic, only: ieee_is_finite
   use stdlib_stats_distribution_uniform, only: pdf_uniform
   implicit none
   real(real64),parameter :: locations(5)=[-2._real64,-0.5_real64,0._real64,0.75_real64,4._real64]
   real(real64),parameter :: widths(5)=[0.125_real64,0.5_real64,1._real64,2._real64,8._real64]
   real(real64) :: x,z,lo,width,expected,actual,previous
   integer :: a,b,i,checks
   checks=0
   do a=1,5
      do b=1,5
         lo=locations(a); width=widths(b); previous=0
         do i=-16,48
            z=real(i,real64)/32
            x=lo+width*z
            expected=0
            if(z>=0.and.z<=1) expected=1/width
            actual=pdf_uniform(x,lo,width)
            call verify(actual,expected)
            checks=checks+1
         end do
      end do
   end do
   print '(a,i0)', 'Uniform references on and outside 25 shifted intervals, including both endpoints: ',checks
   print '(a)', 'PASS stdlib-uniform-pdf-reference'
contains
   subroutine verify(actual,expected)
      real(real64),intent(in) :: actual,expected
      if(.not.ieee_is_finite(actual)) error stop 'Nonfinite distribution result'
      if(actual<0._real64) error stop 'Negative distribution result'
      if(abs(actual-expected)>4.e-15_real64*max(1._real64,abs(expected))) then
         print *, 'actual, expected: ',actual,expected
         error stop 'Independent distribution reference'
      end if
   end subroutine
end program
