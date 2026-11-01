! Independent MIT consumer; see licenses/special-functions-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64, int64
   use ieee_arithmetic, only: ieee_is_finite
   use stdlib_specialfunctions, only: legendre, dlegendre
   implicit none
   real(real64) :: x,p,dp,c
   integer :: n,i,k,power
   do n=0,10
      do i=-16,16
         x=real(i,real64)/16
         p=0; dp=0
         do k=0,n/2
            power=n-2*k
            c=(-1._real64)**k*fact(2*n-2*k)/(2._real64**n*fact(k)*fact(n-k)*fact(power))
            p=p+c*x**power
            if(power>0) dp=dp+power*c*x**(power-1)
         end do
         call verify(legendre(n,x),p,2.e-11_real64)
         call verify(dlegendre(n,x),dp,2.e-11_real64)
      end do
   end do
   print '(a)', '363 Legendre values and 363 derivatives, degrees 0..10, versus explicit polynomial coefficients'
   print '(a)', 'PASS stdlib-legendre-reference'

contains
   subroutine verify(actual,expected,tol)
      real(real64),intent(in) :: actual,expected,tol
      if(.not.ieee_is_finite(actual)) error stop 'Nonfinite result'
      if(abs(actual-expected)>tol*max(1._real64,abs(expected))) then
         print *, 'actual, reference: ',actual,expected
         error stop 'Independent reference mismatch'
      end if
   end subroutine
   function fact(n) result(y)
      integer,intent(in) :: n
      real(real64) :: y
      integer :: j
      y=1
      do j=2,n
         y=y*j
      end do
   end function
end program
