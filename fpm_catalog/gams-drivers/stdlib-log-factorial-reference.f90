! Independent MIT consumer; see licenses/special-functions-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64, int64
   use ieee_arithmetic, only: ieee_is_finite
   use stdlib_specialfunctions_gamma, only: log_factorial
   implicit none
   real(real64) :: expected,actual
   integer(int64) :: n
   expected=0
   do n=0_int64,200_int64
      if(n>1) expected=expected+log(real(n,real64))
      actual=real(log_factorial(n),real64)
      call verify(actual,expected,2.e-6_real64)
   end do
   print '(a)', '201 log-factorials versus summed logarithms; upstream result is REAL32 (tolerance 2e-6)'
   print '(a)', 'PASS stdlib-log-factorial-reference'

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
