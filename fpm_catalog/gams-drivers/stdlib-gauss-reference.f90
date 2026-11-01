! Independent MIT consumer; see licenses/factorization-rules-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64
   use ieee_arithmetic, only: ieee_is_finite
   use stdlib_quadrature, only: gauss_legendre
   implicit none
   real(real64),allocatable :: x(:),w(:),z(:)
   real(real64) :: lo,hi,expected,actual
   integer :: n,interval,p,checks
   checks=0
   do n=2,12
      allocate(x(n),w(n),z(n))
      do interval=1,3
         select case(interval)
         case(1)
            lo=-1
            hi=1
            call gauss_legendre(x,w)
         case(2)
            lo=0
            hi=1
            call gauss_legendre(x,w,interval=[lo,hi])
         case(3)
            lo=-0.5_real64
            hi=1.5_real64
            call gauss_legendre(x,w,interval=[lo,hi])
         end select
         if(.not.all(ieee_is_finite(x)).or..not.all(ieee_is_finite(w))) error stop 'Nonfinite Gauss rule'
         if(any(x<=lo).or.any(x>=hi).or.any(w<=0)) error stop 'Gauss interior/positive weights'
         if(any(x(2:)<=x(:n-1))) error stop 'Gauss node ordering'
         if(maxval(abs(x+x(n:1:-1)-lo-hi))>5.e-12_real64) error stop 'Gauss node symmetry'
         if(maxval(abs(w-w(n:1:-1)))>5.e-12_real64) error stop 'Gauss weight symmetry'
         z=(2*x-lo-hi)/(hi-lo)
         do p=0,2*n-1
            expected=0
            if(mod(p,2)==0) expected=(hi-lo)/real(p+1,real64)
            actual=sum(w*z**p)
            if(abs(actual-expected)>5.e-12_real64*(hi-lo)) error stop 'Gauss analytic moment'
            checks=checks+1
         end do
      end do
      deallocate(x,w,z)
   end do
   print '(a,i0)', '33 Gauss-Legendre rules, orders 2..12; centered monomial moments through degree 2*n-1: ',checks
   print '(a)', 'PASS stdlib-gauss-reference'
end program
