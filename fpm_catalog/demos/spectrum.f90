program main
   use spectrum, only: convolve, remove_mean
   use iso_fortran_env, only: real64
   implicit none
   real(real64), allocatable :: filtered(:), centered(:)
   real(real64) :: signal(3)
   signal = [1.0_real64,2.0_real64,3.0_real64]
   filtered = convolve(signal,[0.5_real64,0.5_real64])
   if (size(filtered) /= 4) error stop 'incorrect convolution length'
   if (maxval(abs(filtered-[0.5_real64,1.5_real64,2.5_real64,1.5_real64])) > 1.e-12_real64) &
      error stop 'incorrect convolution'
   centered = remove_mean(signal)
   if (maxval(abs(centered-[-1.0_real64,0.0_real64,1.0_real64])) > 1.e-12_real64) error stop 'incorrect centering'
   print *, 'Two-point averaging filter (full convolution):', filtered
   print *, 'Signal with mean removed:', centered
   print *, 'PASS spectrum'
end program main
