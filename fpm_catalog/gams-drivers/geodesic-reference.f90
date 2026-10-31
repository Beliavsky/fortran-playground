! Independent API consumer; MIT: licenses/storage-fourier-geometry-drivers-MIT.txt.
program geodesic_reference
   use geodesic_module, only: inverse, direct, wp => geodesic_wp
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   real(wp), parameter :: pi = acos(-1._wp), rad = pi/180, a = 6378137._wp
   real(wp), parameter :: flattening = 1._wp/298.257223563_wp
   real(wp), parameter :: distance_tol = 1.e-6_wp, angle_tol = 1.e-9_wp
   call sphere(10._wp,20._wp,45._wp,80._wp)
   call sphere(-30._wp,170._wp,20._wp,-175._wp)
   call sphere(80._wp,-40._wp,75._wp,130._wp)
   call sphere(-60._wp,-80._wp,-20._wp,100._wp)
   call sphere(0._wp,0._wp,0._wp,90._wp)
   call sphere(35._wp,-120._wp,-12._wp,-60._wp)
   call equator(0._wp,90._wp)
   call equator(170._wp,190._wp)
   call equator(-20._wp,-80._wp)
   call meridian(-40._wp,20._wp)
   call meridian(30._wp,70._wp)
   call meridian(80._wp,85._wp)
   print '(a)', 'PASS geodesic-reference'
contains
   real(wp) function angular_error(x,y)
      real(wp), intent(in) :: x,y
      angular_error = abs(modulo(x-y+180._wp,360._wp)-180._wp)
   end function angular_error

   subroutine compare(lat1,lon1,lat2,lon2,f,expected_distance,expected_azimuth)
      real(wp), intent(in) :: lat1,lon1,lat2,lon2,f,expected_distance,expected_azimuth
      real(wp) :: distance, azi1, azi2, arc, reduced, scale12, scale21, area
      real(wp) :: endpoint_lat, endpoint_lon, final_bearing
      call inverse(a,f,lat1,lon1,lat2,lon2,distance,azi1,azi2,0,arc,reduced,scale12,scale21,area)
      if (.not. all(ieee_is_finite([distance,azi1,azi2]))) error stop 'nonfinite inverse geodesic'
      if (abs(distance-expected_distance) > distance_tol) error stop 'independent geodesic distance'
      if (angular_error(azi1,expected_azimuth) > angle_tol) error stop 'independent initial bearing'
      ! The direct solve uses independent distance and bearing, not inverse outputs.
      call direct(a,f,lat1,lon1,expected_azimuth,expected_distance,0,endpoint_lat,endpoint_lon, &
         final_bearing,0,arc,reduced,scale12,scale21,area)
      if (.not. all(ieee_is_finite([endpoint_lat,endpoint_lon,final_bearing]))) error stop 'nonfinite direct geodesic'
      if (abs(endpoint_lat-lat2) > angle_tol) error stop 'independent endpoint latitude'
      if (angular_error(endpoint_lon,lon2) > angle_tol) error stop 'independent endpoint longitude'
      print '(a,f18.6,a,es9.1)', 'Distance (m): ',distance,' reference error: ',abs(distance-expected_distance)
   end subroutine compare

   subroutine sphere(lat1,lon1,lat2,lon2)
      real(wp), intent(in) :: lat1,lon1,lat2,lon2
      real(wp) :: p,q,d,h,distance,bearing
      p = rad*lat1
      q = rad*lat2
      d = rad*(lon2-lon1)
      h = sin((q-p)/2)**2+cos(p)*cos(q)*sin(d/2)**2
      distance = 2*a*atan2(sqrt(h),sqrt(1._wp-h))
      bearing = atan2(sin(d)*cos(q),cos(p)*sin(q)-sin(p)*cos(q)*cos(d))/rad
      call compare(lat1,lon1,lat2,lon2,0._wp,distance,bearing)
   end subroutine sphere

   subroutine equator(lon1,lon2)
      real(wp), intent(in) :: lon1,lon2
      real(wp) :: delta
      delta = modulo(lon2-lon1+180._wp,360._wp)-180._wp
      call compare(0._wp,lon1,0._wp,lon2,flattening,a*abs(delta)*rad,sign(90._wp,delta))
   end subroutine equator

   subroutine meridian(lat1,lat2)
      real(wp), intent(in) :: lat1,lat2
      real(wp) :: coarse,fine
      coarse = meridian_integral(lat1,lat2,2048)
      fine = meridian_integral(lat1,lat2,4096)
      if (abs(coarse-fine) > distance_tol/10) error stop 'meridional quadrature refinement'
      call compare(lat1,35._wp,lat2,35._wp,flattening,fine,0._wp)
   end subroutine meridian

   real(wp) function meridian_integral(lat1,lat2,panels) result(distance)
      real(wp), intent(in) :: lat1,lat2
      integer, intent(in) :: panels
      real(wp) :: step,e2,latitude,total,term
      integer :: i,weight
      step = (lat2-lat1)*rad/panels
      e2 = flattening*(2-flattening)
      total = 0._wp
      do i = 0,panels
         latitude = lat1*rad+i*step
         term = a*(1-e2)/(1-e2*sin(latitude)**2)**1.5_wp
         weight = 2
         if (mod(i,2) == 1) weight = 4
         if (i == 0 .or. i == panels) weight = 1
         total = total+weight*term
      end do
      distance = total*step/3
   end function meridian_integral
end program geodesic_reference
