! Selected SciFortran integration modules: no MPI or external datasets.
module scifortran_demo_functions
   implicit none
contains
   real(8) function integrand(t)
      real(8) :: t
      integrand = exp(t)
   end function integrand
   real(8) function decay(t)
      real(8) :: t
      decay = exp(-t)
   end function decay
end module scifortran_demo_functions

program main
   use scifortran_demo_functions, only: integrand, decay
   use SF_INTEGRATE, only: simps, trapz, quad
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer, parameter :: n = 101
   integer :: i, key
   real(8) :: x(n), values(n), simpson, trapezoid, adaptive, infinite, rules(6)
   do i = 1, n
      x(i) = real(i-1,8)/real(n-1,8)
   end do
   values = x**3
   simpson = simps(values, 0.0d0, 1.0d0)
   trapezoid = trapz(values, 0.0d0, 1.0d0)
   call quad(integrand, 0.0d0, 1.0d0, epsabs=1.0d-11, epsrel=1.0d-11, result=adaptive)
   call quad(decay, 0.0d0, inf=1, epsabs=1.0d-11, epsrel=1.0d-11, result=infinite)
   do key = 1, 6
      call quad(integrand, 0.0d0, 1.0d0, key=key, epsabs=1.0d-11, epsrel=1.0d-11, result=rules(key))
   end do
   if (.not. all(ieee_is_finite([simpson,trapezoid,adaptive,infinite]))) error stop 'Nonfinite integral'
   if (abs(simpson-0.25d0) > 1.0d-12) error stop 'Simpson cubic integral failed'
   if (abs(trapezoid-0.25d0) > 3.0d-5) error stop 'Trapezoidal integral failed'
   if (abs(adaptive-(exp(1.0d0)-1.0d0)) > 1.0d-10) error stop 'Finite adaptive integral failed'
   if (abs(infinite-1.0d0) > 1.0d-10) error stop 'Infinite adaptive integral failed'
   if (.not. all(ieee_is_finite(rules))) error stop 'Nonfinite Gauss-Kronrod result'
   if (any(abs(rules-(exp(1.0d0)-1.0d0)) > 1.0d-10)) error stop 'Gauss-Kronrod rule failed'
   print '(a,f16.12)', 'Simpson integral of x**3 on [0,1]: ', simpson
   print '(a,f16.12)', 'Trapezoid integral:                ', trapezoid
   print '(a,f16.12)', 'Integral of exp(x) on [0,1]:        ', adaptive
   print '(a,f16.12)', 'Integral of exp(-x) on [0,infinity):', infinite
   print '(a,es12.4)', 'Maximum error for six Gauss-Kronrod rules: ', maxval(abs(rules-(exp(1.0d0)-1.0d0)))
   print '(a)', 'PASS scifortran'
end program main
