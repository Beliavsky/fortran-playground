program jackknife_mean
   use FJsample, only: WP, Complement, jackError
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer, parameter :: n = 6
   real(WP) :: data(n), jack(0:n), error, bias, expected
   data = [1, 2, 4, 5, 8, 10]
   call Complement(jack(0), data)
   call Complement(n, jack(1:), data)
   call jackError(n, jack, error, bias)
   expected = sqrt(sum((data-sum(data)/n)**2)/(n*(n-1)))
   print '(a,f10.6)', 'Sample mean: ', jack(0)
   print '(a,f10.6)', 'Jackknife standard error: ', error
   print '(a,f10.6)', 'Independent standard error: ', expected
   if (.not. ieee_is_finite(error)) error stop 'Nonfinite estimate'
   if (abs(error-expected)>1.e-10_WP .or. abs(bias)>1.e-10_WP) error stop 'Jackknife check'
   print *, 'PASS fjsample'
end program
