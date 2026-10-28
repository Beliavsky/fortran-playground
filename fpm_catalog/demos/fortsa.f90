program time_series_correlations
   use iso_c_binding, only: c_double, c_int
   use fortsa_stats_m, only: acvf, acvf_opt, acvf2acf
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer(c_int), parameter :: n=64, m=9
   real(c_double) :: series(n), centered(n), covariance(m), fft_covariance(m), reference(m)
   integer :: i, lag
   series = [(sin(2*acos(-1.0_c_double)*i/16)+0.3_c_double*cos(2*acos(-1.0_c_double)*i/8),i=0,n-1)]
   centered = series-sum(series)/n
   do lag=0,m-1
      reference(lag+1) = sum(centered(1:n-lag)*centered(1+lag:n))/n
   end do
   call acvf(series,n,covariance,m)
   call acvf_opt(series,n,1_c_int,fft_covariance,m)
   if (.not. all(ieee_is_finite(covariance))) error stop 'Nonfinite covariance'
   if (.not. all(ieee_is_finite(fft_covariance))) error stop 'Nonfinite FFT covariance'
   if (maxval(abs(covariance-reference))>1.e-10_c_double) error stop 'Direct covariance check'
   if (maxval(abs(fft_covariance-reference))>1.e-10_c_double) error stop 'FFT covariance check'
   call acvf2acf(covariance,m)
   if (maxval(abs(covariance-reference/reference(1)))>1.e-10_c_double) error stop 'Correlation check'
   print '(a)', 'Autocorrelation of a generated periodic time series:'
   print '(a)', '  Lag   Correlation'
   do i=1,m
      print '(i5,f14.7)', i-1,covariance(i)
   end do
   print '(a)', 'Direct and FFT estimates agree with independent sums.'
   print *, 'PASS fortsa'
end program
