program demo_fastconv
   use iso_fortran_env, only: real32
   use conv1d_m, only: conv1d_t
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   type(conv1d_t) :: filter
   real(real32) :: signal(6) = [0., 2., 4., 8., 4., 2.]
   real(real32), allocatable :: smoothed(:)

   call filter%set_kernel([0.25_real32, 0.5_real32, 0.25_real32])
   filter%preserve_shape = .false.
   smoothed = filter%apply(signal)
   if (size(smoothed) /= 4) error stop 'Unexpected output size'
   if (.not. all(ieee_is_finite(smoothed))) error stop 'Nonfinite convolution'
   if (maxval(abs(smoothed - [2., 4.5, 6., 4.5])) > 1.e-5_real32) &
      error stop 'Convolution check failed'
   print '(a,*(f6.2))', 'Smoothed signal:', smoothed
   print *, 'PASS fastconv'
end program demo_fastconv
