program approximate_math
   use iso_fortran_env, only: dp => real64
   use fast_exp, only: fexp
   use fast_log, only: flog_quintic
   use fast_rsqrt, only: frsqrt
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   real(dp) :: x(101), positive(101), exp_value(101), log_value(101), rsqrt_value(101)
   real(dp) :: exp_error, log_error, rsqrt_error
   integer :: i
   x = [(-3.0_dp+6.0_dp*i/100,i=0,100)]
   positive = exp(x)
   exp_value = fexp(x)
   log_value = flog_quintic(positive)
   rsqrt_value = frsqrt(positive)
   if (.not. all(ieee_is_finite(exp_value))) error stop 'Nonfinite exponential'
   if (.not. all(ieee_is_finite(log_value))) error stop 'Nonfinite logarithm'
   if (.not. all(ieee_is_finite(rsqrt_value))) error stop 'Nonfinite inverse square root'
   exp_error = maxval(abs(exp_value/exp(x)-1))
   log_error = maxval(abs(log_value-x))
   rsqrt_error = maxval(abs(rsqrt_value*sqrt(positive)-1))
   print '(a)', 'Approximation errors on 101 points, x in [-3,3], positive arguments exp(x):'
   print '(a,es12.4)', 'exp: maximum relative error = ', exp_error
   print '(a,es12.4)', 'log (quintic): maximum absolute error = ', log_error
   print '(a,es12.4)', '1/sqrt: maximum relative error = ', rsqrt_error
   if (exp_error>1.e-4_dp .or. log_error>1.e-3_dp .or. rsqrt_error>2.e-3_dp) error stop 'Accuracy check'
   print *, 'PASS fastmath'
end program
