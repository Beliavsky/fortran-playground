program demo_kissfft
   use kissfft, only: fft, kiss_fft_cpx
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   type(fft) :: transform
   type(kiss_fft_cpx) :: signal(4), spectrum(4), restored(4)
   integer :: i

   do i = 1, 4
      signal(i)%re = real(i)
      signal(i)%im = 0.
   end do
   call transform%init(4, 0)
   call transform%perform(signal, spectrum)
   if (.not. all(ieee_is_finite(spectrum%re)) .or. &
      .not. all(ieee_is_finite(spectrum%im))) error stop 'Nonfinite FFT'
   if (maxval(abs(spectrum%re - [10., -2., -2., -2.])) > 1.e-5) error stop 'FFT real part'
   if (maxval(abs(spectrum%im - [0., 2., 0., -2.])) > 1.e-5) error stop 'FFT imaginary part'
   print *, 'Frequency bin       Real       Imaginary'
   do i = 1, 4
      print '(i8,2f14.6)', i-1, spectrum(i)%re, spectrum(i)%im
   end do
   call transform%init(4, 1)
   call transform%perform(spectrum, restored)
   if (.not. all(ieee_is_finite(restored%re)) .or. &
      .not. all(ieee_is_finite(restored%im))) error stop 'Nonfinite inverse FFT'
   if (maxval(abs(restored%re/4. - signal%re)) > 1.e-5) error stop 'Inverse FFT check'
   if (maxval(abs(restored%im)) > 1.e-5) error stop 'Inverse FFT imaginary part'
   print *, 'Inverse FFT recovered the original signal.'
   print *, 'PASS kissfft-f'
end program demo_kissfft
