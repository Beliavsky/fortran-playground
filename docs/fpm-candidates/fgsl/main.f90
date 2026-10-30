! Draft consumer: the full FGSL module must build before this can be offered.
program main
   use fgsl
   implicit none
   real(fgsl_double) :: value
   value = fgsl_sf_bessel_jc0(0.0_fgsl_double)
   print '(a,f12.8)', 'Bessel J0(0) = ', value
   if (abs(value - 1.0_fgsl_double) > 1.0e-12_fgsl_double) error stop 'Incorrect J0'
   print '(a)', 'PASS fgsl'
end program main
