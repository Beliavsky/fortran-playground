! Independent API consumer; MIT: licenses/lookup-fastmath-drivers-MIT.txt.
program exp_log_reference
   use, intrinsic :: iso_fortran_env, only: dp => real64
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   use fast_exp, only: fexp
   use fast_log, only: flog_quintic
   implicit none
   integer, parameter :: n = 641
   real(dp) :: x(n),positive(n),exponential(n),logarithm(n),exp_error,log_error,identity_error
   integer :: i
   x = [(real(i,dp)/4,i=-320,320)]
   positive = exp(x)
   exponential = fexp(x)
   logarithm = flog_quintic(positive)
   if (.not. all(ieee_is_finite(exponential))) error stop 'nonfinite exponential'
   if (.not. all(ieee_is_finite(logarithm))) error stop 'nonfinite logarithm'
   if (any(exponential <= 0)) error stop 'nonpositive exponential'
   if (any(exponential(2:) <= exponential(:n-1))) error stop 'exponential grid monotonicity'
   if (any(logarithm(2:) <= logarithm(:n-1))) error stop 'logarithm grid monotonicity'
   exp_error = maxval(abs(exponential/positive-1))
   log_error = maxval(abs(logarithm-x))
   if (exp_error > 1.e-4_dp) error stop 'exponential intrinsic reference'
   if (log_error > 1.e-3_dp) error stop 'logarithm inverse reference'
   do i = 1,n
      if (abs(fexp(x(i))/exponential(i)-1) > 1.e-14_dp) error stop 'scalar/array exponential'
      if (abs(flog_quintic(positive(i))-logarithm(i)) > 1.e-12_dp) error stop 'scalar/array logarithm'
   end do
   identity_error = maxval(abs(fexp(logarithm)/positive-1))
   if (.not. ieee_is_finite(identity_error) .or. identity_error > 1.2e-3_dp) error stop 'exp log round trip'
   print '(a)', '641 points x=-80..80 in steps of 0.25; log arguments exp(x).'
   print '(a,es12.4)', 'Maximum exponential relative error versus intrinsic exp: ',exp_error
   print '(a,es12.4)', 'Maximum logarithm absolute error versus x: ',log_error
   print '(a,es12.4)', 'Maximum approximate exp/log round-trip relative error: ',identity_error
   print '(a)', 'Positive exponentials, grid monotonicity and scalar/array consistency checked.'
   print '(a)', 'PASS fastmath-exp-log-reference'
end program exp_log_reference
