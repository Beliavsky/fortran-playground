! Independent MIT consumer; see licenses/special-functions-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64, int64
   use ieee_arithmetic, only: ieee_is_finite
   use stdlib_specialfunctions_gamma, only: beta
   implicit none
   real(real64) :: reference,expected
   integer :: a,b
   do a=1,12
      reference=1._real64/a
      do b=1,12
         expected=reference
         call verify(beta(real(a,real64),real(b,real64)),expected,3.e-12_real64)
         call verify(beta(real(b,real64),real(a,real64)),expected,3.e-12_real64)
         reference=reference*b/(a+b)
      end do
   end do
   print '(a)', '288 beta-family references using independent finite products, shapes 1..12'
   print '(a)', 'PASS stdlib-beta-reference'

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
