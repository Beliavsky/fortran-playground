! Adapted from Formal's extended-gauss-divergence example.
! Copyright (c) 2026, The Regents of the University of California.
! See docs/fpm-candidates/formal/licenses/LICENSE.txt for the upstream terms.
module playground_fields
   implicit none
contains
   pure function scalar(x) result(f)
      real, intent(in) :: x(:)
      real, allocatable :: f(:)
      f = x**2/2
   end function
   pure function vector(x) result(v)
      real, intent(in) :: x(:)
      real, allocatable :: v(:)
      v = x
   end function
end module

program main
   use formal_m, only: scalar_1D_t, vector_1D_t, scalar_1D_initializer_i, vector_1D_initializer_i
   use playground_fields, only: scalar, vector
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   procedure(scalar_1D_initializer_i), pointer :: fs => scalar
   procedure(vector_1D_initializer_i), pointer :: vs => vector
   real :: volume_gradient, volume_divergence, surface, residual

   associate(f => scalar_1D_t(fs, 4, 64, 0.0, 1.0), v => vector_1D_t(vs, 4, 64, 0.0, 1.0))
      associate(dV => f%dV(), dA => v%dA())
         volume_gradient = .SSS. (v .dot. .grad. f) * dV
         volume_divergence = .SSS. (f * .div. v) * dV
         surface = .SS. (f .x. (v .dot. dA))
      end associate
   end associate
   residual = volume_gradient + volume_divergence - surface
   print '(a,f12.8)', 'Integral v grad(f), expected 1/3: ', volume_gradient
   print '(a,f12.8)', 'Integral f div(v), expected 1/6:  ', volume_divergence
   print '(a,f12.8)', 'Boundary flux, expected 1/2:     ', surface
   print '(a,es12.4)', 'Divergence-theorem residual: ', residual
   if (.not. all(ieee_is_finite([volume_gradient, volume_divergence, surface]))) error stop 'nonfinite result'
   if (abs(volume_gradient-1.0/3) > 2e-5 .or. abs(volume_divergence-1.0/6) > 2e-5) error stop 'volume integral'
   if (abs(surface-0.5) > 2e-5 .or. abs(residual) > 2e-5) error stop 'divergence theorem'
   print *, 'PASS formal'
end program
