program demo_ciaaw
   use iso_fortran_env, only: real64
   use ciaaw, only: saw, ice
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   real(real64) :: hydrogen, oxygen, carbon, water, carbon_dioxide, abundance

   ! Use abridged standard atomic weights, rather than interval endpoints.
   hydrogen = saw('H', ab=.true.)
   oxygen = saw('O', ab=.true.)
   carbon = saw('C', ab=.true.)
   if (.not. all(ieee_is_finite([hydrogen,oxygen,carbon]))) error stop 'Nonfinite atomic weights'
   if (abs(hydrogen-1.008_real64) > 0.0001_real64 .or. abs(oxygen-15.999_real64) > 0.001_real64 .or. &
       abs(carbon-12.011_real64) > 0.001_real64) error stop 'Atomic-weight check failed'
   water = 2*hydrogen + oxygen
   carbon_dioxide = carbon + 2*oxygen
   print '(a,f12.5)', 'Water molar mass (g/mol):          ', water
   print '(a,f12.5)', 'Carbon dioxide molar mass (g/mol): ', carbon_dioxide
   abundance = ice('H', A=1) + ice('H', A=2)
   if (.not. ieee_is_finite(abundance)) error stop 'Nonfinite isotope abundance'
   if (abs(abundance-1._real64) > 1.e-6_real64) error stop 'Hydrogen isotope fractions do not sum to one'
   print '(a,f12.8)', 'Hydrogen isotope fractions sum:   ', abundance
   print *, 'PASS ciaaw'
end program demo_ciaaw
