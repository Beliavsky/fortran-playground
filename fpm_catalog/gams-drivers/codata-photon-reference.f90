! Independent MIT consumer; see licenses/state-ten-drivers-MIT.txt.
! Golden values from references/photon_vectors.py, using exact rational SI definitions.
program constants_reference
   use, intrinsic :: iso_fortran_env, only: real64
   use CODATA_2022_constants, only: h=>Planck_constant,c=>speed_of_light_in_vacuum,e=>elementary_charge
   implicit none
   integer, parameter :: wavelengths(*)=[1,2,10,121,250,400,500,656,800,1064,10000,1000000]
   real(real64), parameter :: joules(*)=[ &
      1.98644585714892867e-16_real64, &
      9.93222928574464333e-17_real64, &
      1.98644585714892873e-17_real64, &
      1.64169079103217242e-18_real64, &
      7.94578342859571445e-19_real64, &
      4.96611464287232201e-19_real64, &
      3.97289171429785723e-19_real64, &
      3.02811868467824485e-19_real64, &
      2.48305732143616101e-19_real64, &
      1.86696039205726385e-19_real64, &
      1.98644585714892855e-20_real64, &
      1.98644585714892862e-22_real64 &
      ]
   real(real64), parameter :: ev(*)=[ &
      1.23984198433200254e+03_real64, &
      6.19920992166001270e+02_real64, &
      1.23984198433200262e+02_real64, &
      1.02466279696859726e+01_real64, &
      4.95936793732801018e+00_real64, &
      3.09960496083000647e+00_real64, &
      2.47968396866400509e+00_real64, &
      1.89000302489634553e+00_real64, &
      1.54980248041500324e+00_real64, &
      1.16526502286842359e+00_real64, &
      1.23984198433200257e-01_real64, &
      1.23984198433200262e-03_real64 &
      ]
   real(real64) :: wavelength,energy,error,worst
   integer :: i
   if (h/=6.62607015e-34_real64 .or. c/=299792458.0_real64 .or. e/=1.602176634e-19_real64) &
      error stop 'SI defining constant value'
   worst=0
   do i=1,size(wavelengths)
      wavelength=real(wavelengths(i),real64)*1.e-9_real64
      energy=h*c/wavelength
      error=max(abs(energy/joules(i)-1),abs((energy/e)/ev(i)-1))
      if (error>2.e-15_real64) error stop 'exact rational photon reference'
      worst=max(worst,error)
   end do
   print '(a)', 'Three exact SI constant literals and 24 rational-derived photon-energy references.'
   print '(a,es14.5)', 'Maximum relative photon-energy discrepancy: ',worst
   print '(a)', 'Wavelengths 1..1000000 nm; joules and electron volts checked with independent Python Fraction vectors.'
   print '(a)', 'Selected exact constants only; uncertain CODATA values and the complete constants collection unverified.'
   print '(a)', 'PASS codata-photon-reference'
end program
