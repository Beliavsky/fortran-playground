! Example: Numerical: complex-step differentiation
! Adapted from https://github.com/Beliavsky/FortranTip/blob/main/complex_step.f90
! Try h = 1.0e-2_real64, then reduce it; compare cancellation errors.
! For analytic functions, f'(x) is approximately aimag(f(x+i*h))/h.
program complex_step_derivative
   use, intrinsic :: iso_fortran_env, only: real64
   implicit none
   real(real64), parameter :: h = 1.0e-10_real64
   real(real64) :: complex_estimate, central_estimate
   complex_estimate = aimag(exp(cmplx(0.0_real64,h,kind=real64)))/h
   central_estimate = (exp(h)-exp(-h))/(2*h)
   print '(a,f18.12)', 'Complex-step derivative of exp at 0: ', complex_estimate
   print '(a,f18.12)', 'Central-difference derivative: ', central_estimate
   print '(a,f18.12)', 'Exact derivative: ', 1.0_real64
end program complex_step_derivative
