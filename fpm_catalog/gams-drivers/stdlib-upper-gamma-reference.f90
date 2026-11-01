! Independent MIT consumer; see licenses/special-functions-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64, int64
   use ieee_arithmetic, only: ieee_is_finite
   use stdlib_specialfunctions_gamma, only: upper_incomplete_gamma
   implicit none
   real(real64) :: x,s,term,factor,q,p,actual
   integer :: n,i,k,checks
   checks=0
   factor=1
   do n=1,8
      if(n>1) factor=factor*(n-1)
      do i=0,32
         x=real(i,real64)/4
         s=1; term=1
         do k=1,n-1
            term=term*x/k
            s=s+term
         end do
         q=exp(-x)*s
         p=1-q
         actual=upper_incomplete_gamma(real(n,real64),x)
         call verify(actual,factor*q,3.e-12_real64)
         checks=checks+1
      end do
   end do
   print '(a,i0)', 'Finite Poisson-sum reference pairs (integer-valued REAL64 shapes 1..8, x=0..8): ',checks
   print '(a)', 'PASS stdlib-upper-gamma-reference'

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
