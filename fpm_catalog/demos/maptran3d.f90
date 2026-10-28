program demo_maptran3d
   use iso_fortran_env, only: real64
   use maptran, only: geodetic2ecef, ecef2geodetic
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   real(real64) :: latitude, longitude, altitude, x, y, z, lat2, lon2, alt2

   latitude = 40.7128_real64
   longitude = -74.0060_real64
   altitude = 15._real64
   call geodetic2ecef(latitude, longitude, altitude, x, y, z, deg=.true.)
   if (.not. all(ieee_is_finite([x,y,z]))) error stop 'Nonfinite Cartesian coordinates'
   call ecef2geodetic(x, y, z, lat2, lon2, alt2, deg=.true.)
   if (.not. all(ieee_is_finite([lat2,lon2,alt2]))) error stop 'Nonfinite geographic coordinates'
   if (abs(lat2-latitude) > 1.e-7_real64 .or. abs(lon2-longitude) > 1.e-7_real64 .or. &
       abs(alt2-altitude) > 1.e-3_real64) error stop 'Coordinate round trip failed'
   print '(a,3f17.5)', 'Earth-centered coordinates (m):', x, y, z
   print '(a,2f14.7,f12.4)', 'Recovered latitude, longitude, altitude:', lat2, lon2, alt2
   ! Independent WGS84 reference: zero latitude/longitude lies on the x axis.
   call geodetic2ecef(0._real64, 0._real64, 0._real64, x, y, z, deg=.true.)
   if (maxval(abs([x-6378137._real64,y,z])) > 1.e-6_real64) error stop 'WGS84 equator check'
   print *, 'PASS maptran3d'
end program demo_maptran3d
