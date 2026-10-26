program main
   use fftpack, only: fft, ifft, rk
   implicit none
   complex(rk) :: x(4), y(4), restored(4)
   x = cmplx([1, 2, 3, 4], 0, kind=rk)
   y = fft(x)
   ! FFTPACK's backward transform is unnormalized.
   restored = ifft(y) / real(size(x), rk)
   if (maxval(abs(restored-x)) > 1.0e-10_rk) error stop 'FFT round trip failed'
   print *, 'Fourier coefficients:', y
   print *, 'PASS fftpack'
end program main
