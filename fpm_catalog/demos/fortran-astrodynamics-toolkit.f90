program main
   use fortran_astrodynamics_toolkit, only: orbital_elements_to_rv, fat_wp
   implicit none
   real(fat_wp), parameter :: mu=398600.4418_fat_wp, radius=7000.0_fat_wp
   real(fat_wp) :: r(3), v(3)
   ! Circular equatorial orbit: semilatus rectum equals the radius.
   call orbital_elements_to_rv(mu,radius,0.0_fat_wp,0.0_fat_wp, &
      0.0_fat_wp,0.0_fat_wp,0.0_fat_wp,r,v)
   if (abs(norm2(r)-radius) > 1.e-8_fat_wp) error stop 'incorrect radius'
   if (abs(norm2(v)-sqrt(mu/radius)) > 1.e-10_fat_wp) error stop 'incorrect speed'
   if (abs(dot_product(r,v)) > 1.e-8_fat_wp) error stop 'velocity is not tangential'
   print *, 'Position (km):', r
   print *, 'Velocity (km/s):', v
   print *, 'PASS fortran-astrodynamics-toolkit'
end program
