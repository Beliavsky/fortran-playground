program main
   use iso_fortran_env, only: real64
   use CODATA_2022_constants, only: h=>Planck_constant, &
      c=>speed_of_light_in_vacuum, e=>elementary_charge
   implicit none
   real(real64) :: wavelength, energy, electron_volts
   wavelength = 500.0e-9_real64
   energy = h*c/wavelength
   electron_volts = energy/e
   if (abs(energy-3.972891714297857e-19_real64) > 1.0e-32_real64) error stop 'energy in joules'
   if (abs(electron_volts-2.479683968664005_real64) > 1.0e-12_real64) error stop 'energy in eV'
   print '(a)', 'CODATA 2022: photon with wavelength 500 nm'
   print '(a,es22.14)', 'Energy in joules: ', energy
   print '(a,f16.12)', 'Energy in electron volts: ', electron_volts
   print *, 'PASS fundamental_constants'
end program
