program main
   use iso_fortran_env, only: real64
   use astro_module, only: G2ICRS,ICRS2G
   implicit none
   real(real64) :: longitude,latitude,ra,dec,back_l,back_b
   longitude=5.5850536063818546461558105_real64
   latitude=-.7853981633974483096156608_real64
   call G2ICRS(longitude,latitude,ra,dec)
   ! Reference values from the upstream SOFA validation example.
   if (abs(ra-5.9338074302227188048671_real64)>1e-12_real64) error stop
   if (abs(dec+1.1784870613579944551541_real64)>1e-12_real64) error stop
   call ICRS2G(ra,dec,back_l,back_b)
   if (max(abs(back_l-longitude),abs(back_b-latitude))>1e-12_real64) error stop
   print *, 'Galactic coordinates -> ICRS, angles in radians'
   print '(a,2f18.12)', 'Longitude, latitude:',longitude,latitude
   print '(a,2f18.12)', 'RA, declination:    ',ra,dec
   print *, 'PASS astro-fortran'
end program main
