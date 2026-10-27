program main
   use codata, only: SPEED_OF_LIGHT_IN_VACUUM, PLANCK_CONSTANT, BOLTZMANN_CONSTANT
   use iso_fortran_env, only: real64
   implicit none
   real(real64) :: wavelength, energy, temperature
   wavelength = 500.e-9_real64
   energy = PLANCK_CONSTANT%value*SPEED_OF_LIGHT_IN_VACUUM%value/wavelength
   temperature = energy/BOLTZMANN_CONSTANT%value
   if (abs(SPEED_OF_LIGHT_IN_VACUUM%value-299792458.0_real64) > 1.e-6_real64) error stop 'incorrect light speed'
   if (abs(energy/3.972891714297857e-19_real64-1.0_real64) > 1.e-12_real64) error stop 'incorrect photon energy'
   print *, '500 nm photon energy (J):', energy
   print *, 'Equivalent E/k temperature (K):', temperature
   print *, 'Planck constant uncertainty:', PLANCK_CONSTANT%uncertainty
   print *, 'PASS codata'
end program main
