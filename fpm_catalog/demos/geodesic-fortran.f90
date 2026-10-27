program main
   use geodesic_module, only: inverse, direct, wp => geodesic_wp
   implicit none
   real(wp), parameter :: a=6378137._wp, f=1._wp/298.257223563_wp
   real(wp) :: distance, azimuth1, azimuth2, arc, reduced, scale12, scale21, area
   real(wp) :: latitude, longitude, final_bearing
   ! Equatorial quarter-circle: distance must equal pi*a/2.
   call inverse(a,f,0._wp,0._wp,0._wp,90._wp,distance,azimuth1,azimuth2, &
      0,arc,reduced,scale12,scale21,area)
   if (abs(distance-acos(-1._wp)*a/2)>1.e-6_wp) error stop 'incorrect equatorial distance'
   ! London to New York, with a direct/inverse round trip.
   call inverse(a,f,51.5074_wp,-0.1278_wp,40.7128_wp,-74.0060_wp, &
      distance,azimuth1,azimuth2,0,arc,reduced,scale12,scale21,area)
   if (distance < 5.58e6_wp .or. distance > 5.59e6_wp) error stop 'incorrect city distance'
   call direct(a,f,51.5074_wp,-0.1278_wp,azimuth1,distance,0,latitude,longitude, &
      final_bearing,0,arc,reduced,scale12,scale21,area)
   if (abs(latitude-40.7128_wp)>1.e-8_wp .or. abs(longitude+74.0060_wp)>1.e-8_wp) &
      error stop 'failed geodesic round trip'
   print *, 'London to New York (km):',distance/1000
   print *, 'Initial and final bearings (degrees):',azimuth1,azimuth2
   print *, 'PASS geodesic-fortran'
end program main
