program main
   use peaks, only: peak_detect
   use iso_fortran_env, only: real64
   implicit none
   integer, allocatable :: maxima(:), minima(:)
   real(real64), allocatable :: high(:), low(:)
   real(real64) :: signal(9)
   signal = [0.0_real64,1.0_real64,3.0_real64,1.0_real64,0.0_real64, &
             1.0_real64,4.0_real64,1.0_real64,0.0_real64]
   call peak_detect(signal,0.5_real64,maxima,high,minima,low)
   if (size(maxima) /= 2 .or. size(minima) /= 1) error stop 'incorrect extrema count'
   if (any(maxima /= [3,7]) .or. any(minima /= [5])) error stop 'incorrect extrema positions'
   if (maxval(abs(high-[3.0_real64,4.0_real64])) > 1.e-12_real64) error stop 'incorrect peak values'
   print *, 'Peak positions:', maxima
   print *, 'Peak heights:', high
   print *, 'Valley position:', minima
   print *, 'PASS peaks'
end program main
