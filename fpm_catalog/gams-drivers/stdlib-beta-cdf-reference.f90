! Independent MIT consumer; see licenses/distribution-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64
   use ieee_arithmetic, only: ieee_is_finite
   use stdlib_stats_distribution_beta, only: cdf_beta
   implicit none
   real(real64),parameter :: locations(3)=[-1.5_real64,0._real64,2.25_real64]
   real(real64) :: x,z,expected,actual,previous,coefficient
   integer :: a,b,i,j,k,n,l,checks
   checks=0
   do a=2,7
      do b=2,7
         n=a+b-1
         do l=1,3
            previous=0
            do i=-4,36
               z=real(i,real64)/32
               x=locations(l)+z
               expected=0
               if(z>=1) expected=1
               if(z>0.and.z<1) then
                  do j=a,n
                     coefficient=1
                     do k=1,j
                        coefficient=coefficient*real(n-k+1,real64)/k
                     end do
                     expected=expected+coefficient*z**j*(1-z)**(n-j)
                  end do
               end if
               actual=cdf_beta(x,real(a,real64),real(b,real64),loc=locations(l))
               call verify(actual,expected)
               checks=checks+1
            end do
         end do
      end do
   end do
   print '(a,i0)', 'Shifted beta references for integer shapes 2..7, three locations and 41 support/boundary points: ',checks
   print '(a)', 'PASS stdlib-beta-cdf-reference'
contains
   subroutine verify(actual,expected)
      real(real64),intent(in) :: actual,expected
      if(.not.ieee_is_finite(actual)) error stop 'Nonfinite distribution result'
      if(actual<0._real64) error stop 'Negative distribution result'
      if(abs(actual-expected)>3.e-12_real64*max(1._real64,abs(expected))) then
         print *, 'actual, expected: ',actual,expected
         error stop 'Independent distribution reference'
      end if
      if(actual>1._real64) error stop 'CDF exceeds one'
      if(actual+3.e-14_real64<previous) error stop 'Nonmonotone CDF'
      previous=actual
   end subroutine
end program
