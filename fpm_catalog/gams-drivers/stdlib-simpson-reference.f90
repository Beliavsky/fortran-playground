! Independent MIT consumer; see licenses/factorization-rules-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64
   use ieee_arithmetic, only: ieee_is_finite
   use stdlib_quadrature, only: simps
   implicit none
   real(real64) :: x(33),y(33),a,b,c,d,lo,hi,expected,actual
   integer :: n,t,i,checks
   checks=0
   do n=3,33,2
      do t=-4,4
         a=real(t,real64)/8
         b=real(n-17,real64)/16
         c=0.25_real64
         d=-0.5_real64
         do i=1,n
            x(i)=real(i-1,real64)/16-1
         end do
         y(:n)=a*x(:n)**3+b*x(:n)**2+c*x(:n)+d
         lo=x(1)
         hi=x(n)
         expected=a*(hi**4-lo**4)/4+b*(hi**3-lo**3)/3+c*(hi**2-lo**2)/2+d*(hi-lo)
         actual=simps(y(:n),x(:n))
         call verify()
         actual=simps(y(:n),0.0625_real64)
         call verify()
         do i=1,n
            x(i)=real((i-1)**2,real64)/512-1
         end do
         y(:n)=a*x(:n)**2+c*x(:n)+d
         lo=x(1)
         hi=x(n)
         expected=a*(hi**3-lo**3)/3+c*(hi**2-lo**2)/2+d*(hi-lo)
         actual=simps(y(:n),x(:n))
         call verify()
      end do
   end do
   print '(a,i0)', 'Odd grids, lengths 3..33; uniform cubics and nonuniform quadratics versus antiderivatives: ',checks
   print '(a)', 'PASS stdlib-simpson-reference'
contains
   subroutine verify()
      if(.not.ieee_is_finite(actual)) error stop 'Nonfinite Simpson result'
      if(abs(actual-expected)>2.e-12_real64*max(1._real64,abs(expected))) error stop 'Polynomial integral oracle'
      checks=checks+1
   end subroutine
end program
