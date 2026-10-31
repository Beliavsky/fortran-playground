! Independent API consumer; see licenses/expressions-sky-drivers-MIT.txt.
program checked_sky_coordinates
   use iso_fortran_env, only: real64
   use astro_module, only: G2ICRS,ICRS2G
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
   real(real64), parameter :: pi=acos(-1.0_real64),degree=pi/180
   real(real64), parameter :: pole_ra=192.85948_real64*degree,pole_dec=27.12825_real64*degree
   real(real64), parameter :: node=32.93192_real64*degree
   real(real64), parameter :: latitudes(9)=[-90.0_real64,-75.0_real64,-45.0_real64,-10.0_real64, &
      0.0_real64,10.0_real64,45.0_real64,75.0_real64,90.0_real64]*degree
   integer, parameter :: wraps(3)=[-2,0,3]
   real(real64) :: longitude,latitude,out_lon,out_lat,back_lon,back_lat,input(3),reference(3),output(3),back(3)
   real(real64) :: error,worst_direct=0,worst_roundtrip=0,worst_norm=0
   integer :: frame,i,j,k,samples=0,calls=0
   do frame=1,2
      do i=0,23
         do j=1,9
            do k=1,3
               longitude=2*pi*(real(i,real64)/24+wraps(k)); latitude=latitudes(j)
               input=unit(longitude,latitude); reference=input
               if (frame==1) then
                  ! ICRS -> Galactic, using three separately applied passive rotations.
                  call rotate_z(reference,pi/2+pole_ra)
                  call rotate_x(reference,pi/2-pole_dec)
                  call rotate_z(reference,-node)
                  call ICRS2G(longitude,latitude,out_lon,out_lat)
                  call G2ICRS(out_lon,out_lat,back_lon,back_lat)
               else
                  call rotate_z(reference,node)
                  call rotate_x(reference,pole_dec-pi/2)
                  call rotate_z(reference,-pi/2-pole_ra)
                  call G2ICRS(longitude,latitude,out_lon,out_lat)
                  call ICRS2G(out_lon,out_lat,back_lon,back_lat)
               end if
               call check_angles(out_lon,out_lat); call check_angles(back_lon,back_lat)
               output=unit(out_lon,out_lat); back=unit(back_lon,back_lat)
               error=norm2(output-reference); worst_direct=max(worst_direct,error)
               if (error>2e-12_real64) error stop 'independent sky rotation mismatch'
               error=norm2(back-input); worst_roundtrip=max(worst_roundtrip,error)
               if (error>2e-12_real64) error stop 'sky roundtrip vector mismatch'
               error=max(abs(norm2(output)-1),abs(norm2(back)-1)); worst_norm=max(worst_norm,error)
               if (error>2e-12_real64) error stop 'unit vector normalization'
               samples=samples+1; calls=calls+2
            end do
         end do
      end do
   end do
   print '(a,i0)', 'Sky direction fixtures: ',samples
   print '(a,i0)', 'Forward/inverse conversion calls: ',calls
   print '(a,i0)', 'Independent rotation vector references: ',samples
   print '(a,es12.4)', 'Maximum direct vector discrepancy: ',worst_direct
   print '(a,es12.4)', 'Maximum roundtrip vector discrepancy: ',worst_roundtrip
   print '(a,es12.4)', 'Maximum unit-norm error: ',worst_norm
   print '(a)', 'PASS astro-sky-reference'
contains
   function unit(longitude,latitude) result(v)
      real(real64), intent(in) :: longitude,latitude
      real(real64) :: v(3)
      v=[cos(latitude)*cos(longitude),cos(latitude)*sin(longitude),sin(latitude)]
   end function unit
   subroutine rotate_z(v,angle)
      real(real64), intent(inout) :: v(3)
      real(real64), intent(in) :: angle
      real(real64) :: x,y
      x=v(1); y=v(2)
      v(1)=cos(angle)*x+sin(angle)*y; v(2)=-sin(angle)*x+cos(angle)*y
   end subroutine rotate_z
   subroutine rotate_x(v,angle)
      real(real64), intent(inout) :: v(3)
      real(real64), intent(in) :: angle
      real(real64) :: y,z
      y=v(2); z=v(3)
      v(2)=cos(angle)*y+sin(angle)*z; v(3)=-sin(angle)*y+cos(angle)*z
   end subroutine rotate_x
   subroutine check_angles(longitude,latitude)
      real(real64), intent(in) :: longitude,latitude
      if (.not.all(ieee_is_finite([longitude,latitude]))) error stop 'nonfinite sky angles'
      ! Wrapping a tiny negative angle can round to exactly 2*pi.
      if (longitude<(-64*epsilon(pi)).or.longitude>2*pi+64*epsilon(pi)) error stop 'longitude range'
      if (abs(latitude)>pi/2+64*epsilon(pi)) error stop 'latitude range'
   end subroutine check_angles
end program checked_sky_coordinates
