program demo_gaussjacobiquad
   use GaussJacobiQuad, only: gauss_jacobi
   use gjp_types, only: dp
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   real(dp) :: x(5), w(5), integral
   character(:), allocatable :: method

   ! Integral of (1-x)*(1+x)*x**2 over [-1,1] is 4/15.
   method = 'gw'
   call gauss_jacobi(5, 1._dp, 1._dp, x, w, method)
   integral = sum(w*x**2)
   if (.not. ieee_is_finite(integral)) error stop 'Nonfinite integral'
   if (abs(integral - 4._dp/15._dp) > 1.e-12_dp) error stop 'Quadrature check failed'
   if (any(w <= 0._dp) .or. any(abs(x) >= 1._dp)) error stop 'Invalid nodes or weights'
   print '(a,f18.14)', 'Weighted integral of x squared: ', integral
   print *, 'PASS gaussjacobiquad'
end program demo_gaussjacobiquad
