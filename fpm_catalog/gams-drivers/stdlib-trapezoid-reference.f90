! Independent MIT consumer; see licenses/statistics-services-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64
   use ieee_arithmetic, only: ieee_is_finite
   use stdlib_quadrature, only: trapz
   implicit none
   real(real64) :: x(33),y(33),a,b,slope,constant,actual,expected
   integer :: n,i,k,checks
   checks=0
   do n=2,33
      do k=-4,4
         slope=real(k,real64)/4
         constant=real(n-17,real64)/8
         do i=1,n
            x(i)=real((i-1)**2,real64)/64-2
         end do
         y(:n)=slope*x(:n)+constant
         a=x(1)
         b=x(n)
         expected=slope*(b*b-a*a)/2+constant*(b-a)
         actual=trapz(y(:n),x(:n))
         call verify()
         actual=trapz(y(n:1:-1),x(n:1:-1))
         expected=-expected
         call verify()
         do i=1,n
            x(i)=real(i-1,real64)/8-2
         end do
         y(:n)=slope*x(:n)+constant
         a=x(1)
         b=x(n)
         expected=slope*(b*b-a*a)/2+constant*(b-a)
         actual=trapz(y(:n),0.125_real64)
         call verify()
      end do
   end do
   print '(a,i0)', 'Affine antiderivatives on nonuniform, reversed and constant-spacing grids: ',checks
   print '(a)', 'PASS stdlib-trapezoid-reference'
contains
   subroutine verify()
      if(.not.ieee_is_finite(actual).or.actual/=expected) error stop 'Affine integral oracle'
      checks=checks+1
   end subroutine
end program
