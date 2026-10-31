! Independent API consumer; MIT: licenses/geodesy-forlab-drivers-MIT.txt.
program main
   use iso_fortran_env,only:wp=>real64
   use ieee_arithmetic,only:ieee_is_finite
   use maptran,only:geodetic2ecef,ecef2geodetic
   implicit none
   real(wp),parameter::pi=acos(-1.0_wp),a=6378137.0_wp,flattening=1/298.257223563_wp
   real(wp),parameter::eccentricity2=flattening*(2-flattening),b=a*(1-flattening)
   real(wp),parameter::latitudes(*)=[-89.0_wp,-60.0_wp,-30.0_wp,0.0_wp,30.0_wp,60.0_wp,89.0_wp]
   real(wp),parameter::longitudes(*)=[-180.0_wp,-90.0_wp,-23.0_wp,0.0_wp,74.0_wp,180.0_wp]
   real(wp),parameter::heights(*)=[-100.0_wp,0.0_wp,1000.0_wp,100000.0_wp]
   real(wp)::lat,lon,h,p,l,radius,reference(3),xyz(3),input(3),saved(3),back(3)
   real(wp)::position_error,angular_error,height_error,worst_p,worst_a,worst_h
   integer::il,io,ih,mode,sign,cases,calls,pole_calls
   logical::degrees
   cases=0; calls=0; pole_calls=0; worst_p=0; worst_a=0; worst_h=0
   do il=1,size(latitudes)
      lat=latitudes(il); p=lat*pi/180
      radius=a/sqrt(1-eccentricity2*sin(p)**2)
      do io=1,size(longitudes)
         lon=longitudes(io); l=lon*pi/180
         do ih=1,size(heights)
            h=heights(ih)
            reference=[(radius+h)*cos(p)*cos(l),(radius+h)*cos(p)*sin(l), &
               (radius*(1-eccentricity2)+h)*sin(p)]
            do mode=1,2
               degrees=mode==1
               input=[lat,lon,h]
               if (.not.degrees) input(:2)=input(:2)*pi/180
               saved=input
               call geodetic2ecef(input(1),input(2),input(3),xyz(1),xyz(2),xyz(3),deg=degrees)
               if (.not.all(ieee_is_finite(xyz))) error stop 'nonfinite ECEF'
               if (any(input/=saved)) error stop 'changed geodetic input'
               position_error=maxval(abs(xyz-reference))
               if (position_error>5e-6_wp) error stop 'independent WGS84 forward reference'
               ! Feed the independent Cartesian reference, not the library's forward output.
               call ecef2geodetic(reference(1),reference(2),reference(3),back(1),back(2),back(3),deg=degrees)
               if (.not.all(ieee_is_finite(back))) error stop 'nonfinite inverse'
               if (.not.degrees) back(:2)=back(:2)*180/pi
               angular_error=max(abs(back(1)-lat), &
                  abs(atan2(sin((back(2)-lon)*pi/180),cos((back(2)-lon)*pi/180)))*180/pi)
               height_error=abs(back(3)-h)
               if (angular_error>2e-7_wp.or.height_error>5e-3_wp) error stop 'independent WGS84 inverse reference'
               worst_p=max(worst_p,position_error); worst_a=max(worst_a,angular_error)
               worst_h=max(worst_h,height_error)
               calls=calls+2; cases=cases+1
            end do
         end do
      end do
   end do
   ! At the poles only the forward map is checked; longitude there is not unique.
   do sign=-1,1,2
      do ih=2,3
         h=heights(ih)
         do mode=1,2
            degrees=mode==1
            lat=sign*90.0_wp
            if (.not.degrees) lat=lat*pi/180
            call geodetic2ecef(lat,0.0_wp,h,xyz(1),xyz(2),xyz(3),deg=degrees)
            if (.not.all(ieee_is_finite(xyz))) error stop 'nonfinite pole'
            if (maxval(abs(xyz-[0.0_wp,0.0_wp,sign*(b+h)]))>5e-6_wp) error stop 'exact polar axis'
            calls=calls+1; pole_calls=pole_calls+1
         end do
      end do
   end do
   if (cases/=336.or.calls/=680.or.pole_calls/=8) error stop 'accounting'
   print '(a,i0,a,i0)', 'Degree/radian geodetic cases: ',cases,'; conversion calls: ',calls
   print '(a,i0)', 'Additional exact forward polar-axis calls: ',pole_calls
   print '(a,es12.4)', 'Maximum ECEF error (meters): ',worst_p
   print '(a,es12.4)', 'Maximum inverse angular error (degrees): ',worst_a
   print '(a,es12.4)', 'Maximum inverse height error (meters): ',worst_h
   print '(a)', 'PASS maptran-wgs84-reference'
end program
