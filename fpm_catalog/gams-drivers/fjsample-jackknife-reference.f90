! Independent API consumer; see licenses/resampling-markov-drivers-MIT.txt.
program jackknife_reference
   use FJsample, only: WP, Complement, jackError
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   real(WP), parameter :: tol = 1.e-11_WP
   call check([1._WP, 3._WP])
   call check([1._WP, 2._WP, 4._WP, 5._WP, 8._WP, 10._WP])
   call check([7._WP, 7._WP, 7._WP, 7._WP])
   call check([-1._WP, -3._WP, -7._WP, -9._WP, -15._WP, -19._WP])
   call check([-4._WP, -3._WP, -2._WP, -1._WP, 1._WP, 2._WP, 3._WP, 4._WP])
   print '(a)', 'PASS fjsample-jackknife-reference'
contains
   subroutine check(data)
      real(WP), intent(in) :: data(:)
      real(WP) :: jack(0:size(data)), reference(size(data)), nonlinear(0:size(data))
      real(WP) :: mean, variance, se, bias, se_ref, bias_ref, total, average, err
      integer :: n, i, j
      n = size(data)
      mean = 0._WP
      do i = 1, n
         mean = mean + data(i)/n
         total = 0._WP
         do j = 1, n
            if (j /= i) total = total + data(j)
         end do
         reference(i) = total/(n-1)
      end do
      variance = 0._WP
      do i = 1, n
         variance = variance + (data(i)-mean)**2/(n-1)
      end do
      call Complement(jack(0), data)
      call Complement(n, jack(1:), data)
      if (.not. all(ieee_is_finite(jack))) error stop 'nonfinite complement'
      err = max(abs(jack(0)-mean), maxval(abs(jack(1:)-reference)))
      if (err > tol) error stop 'independent leave-one-out means'
      call jackError(n, jack, se, bias)
      se_ref = sqrt(variance/n)
      if (.not. all(ieee_is_finite([se, bias]))) error stop 'nonfinite mean uncertainty'
      if (abs(se-se_ref) > tol .or. abs(bias) > tol) error stop 'sample mean standard error or bias'
      print '(a,i2,a,f9.4,a,f10.6)', 'n=', n, ' mean=', mean, ' standard error=', se

      ! A nonlinear estimator: square the sample mean and each resampled mean.
      nonlinear = jack**2
      call jackError(n, nonlinear, se, bias)
      average = 0._WP
      do i = 1, n
         average = average + reference(i)**2/n
      end do
      total = 0._WP
      do i = 1, n
         total = total + (reference(i)**2-average)**2
      end do
      se_ref = sqrt(real(n-1, WP)/n*total)
      ! Package bias is full estimate minus mean resampled estimate, without (n-1).
      ! For this estimator it equals -sample_variance/(n*(n-1)).
      bias_ref = -variance/(real(n, WP)*(n-1))
      if (.not. all(ieee_is_finite([se, bias]))) error stop 'nonfinite nonlinear uncertainty'
      if (abs(se-se_ref) > tol .or. abs(bias-bias_ref) > tol) error stop 'squared mean uncertainty or bias'
      print '(a,f11.6,a,f11.6)', '  squared mean standard error=', se, ' package bias=', bias
   end subroutine check
end program jackknife_reference
