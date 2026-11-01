! Independent MIT consumer; see licenses/special-functions-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64, int64
   use ieee_arithmetic, only: ieee_is_finite
   use stdlib_specialfunctions_gamma, only: incomplete_beta
   implicit none
   real(real64) :: x,expected,coefficient,actual
   integer :: a,b,i,j,n,k
   do a=1,8
      do b=1,8
         n=a+b-1
         do i=0,32
            x=real(i,real64)/32
            expected=0
            do j=a,n
               coefficient=1
               do k=1,j
                  coefficient=coefficient*real(n-k+1,real64)/k
               end do
               expected=expected+coefficient*x**j*(1-x)**(n-j)
            end do
            actual=incomplete_beta(x,real(a,real64),real(b,real64))
            call verify(actual,expected,5.e-12_real64)
         end do
      end do
   end do
   print '(a)', '2112 regularized incomplete-beta references versus independent binomial tail sums'
   print '(a)', 'PASS stdlib-incomplete-beta-reference'

contains
   subroutine verify(actual,expected,tol)
      real(real64),intent(in) :: actual,expected,tol
      if(.not.ieee_is_finite(actual)) error stop 'Nonfinite result'
      if(abs(actual-expected)>tol*max(1._real64,abs(expected))) then
         print *, 'actual, reference: ',actual,expected
         error stop 'Independent reference mismatch'
      end if
   end subroutine
end program
