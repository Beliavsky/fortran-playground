! Independent API consumer; MIT: licenses/quantities-spherical-drivers-MIT.txt.
program zonal_reference
   use spherepack, only: GaussianSphere,wp,ip
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer(ip), parameter :: latitudes(*) = [9,13,17],longitudes(*) = [16,24,32]
   type(GaussianSphere) :: globe
   real(wp), allocatable :: field(:,:),synthesized(:,:),z(:,:),expected_a(:,:)
   real(wp) :: amplitudes(0:4),max_coefficient_error,max_round_trip_error,max_injected_error,error
   integer :: grid,fixture,nlat,nlon,l,m,i,j,cases
   max_coefficient_error = 0._wp
   max_round_trip_error = 0._wp
   max_injected_error = 0._wp
   cases = 0
   do grid = 1,3
      nlat = latitudes(grid)
      nlon = longitudes(grid)
      globe = GaussianSphere(nlat,nlon)
      allocate(field(nlat,nlon),synthesized(nlat,nlon),z(nlat,nlon),expected_a(nlat,nlat))
      do j = 1,nlon
         do i = 1,nlat
            z(i,j) = globe%unit_vectors%radial(i,j)%z
         end do
      end do
      do fixture = 0,5
         amplitudes = 0._wp
         if (fixture <= 4) then
            amplitudes(fixture) = 1._wp
         else
            amplitudes = [1._wp,-2._wp,.5_wp,.25_wp,-.75_wp]
         end if
         field = amplitudes(0)+amplitudes(1)*z+amplitudes(2)*(3*z*z-1)/2 &
            +amplitudes(3)*(5*z**3-3*z)/2+amplitudes(4)*(35*z**4-30*z*z+3)/8
         expected_a = 0._wp
         do l = 0,4
            ! Spherepack's m=0 half-weight and normalized Legendre basis.
            expected_a(1,l+1) = 2*sqrt(2._wp/real(2*l+1,wp))*amplitudes(l)
         end do
         globe%workspace%scalar_coefficients%real_component = 0._wp
         globe%workspace%scalar_coefficients%imaginary_component = 0._wp
         call globe%perform_scalar_analysis(field)
         do l = 0,nlat-1
            do m = 0,min(l,(nlon-1)/2)
               error = abs(globe%workspace%scalar_coefficients%real_component(m+1,l+1)-expected_a(m+1,l+1))
               if (.not. ieee_is_finite(error)) error stop 'nonfinite real harmonic coefficient'
               max_coefficient_error = max(max_coefficient_error,error)
               error = abs(globe%workspace%scalar_coefficients%imaginary_component(m+1,l+1))
               if (.not. ieee_is_finite(error)) error stop 'nonfinite imaginary harmonic coefficient'
               max_coefficient_error = max(max_coefficient_error,error)
            end do
         end do
         if (max_coefficient_error > 2.e-11_wp) error stop 'independent Legendre coefficient reference'
         call globe%perform_scalar_synthesis(synthesized)
         if (.not. all(ieee_is_finite(synthesized))) error stop 'nonfinite spherical round trip'
         max_round_trip_error = max(max_round_trip_error,maxval(abs(synthesized-field)))
         if (max_round_trip_error > 2.e-11_wp) error stop 'spherical round trip'
         ! Erase the analyzed data: independently inject exact coefficients before synthesis.
         globe%workspace%scalar_coefficients%real_component = expected_a
         globe%workspace%scalar_coefficients%imaginary_component = 0._wp
         call globe%perform_scalar_synthesis(synthesized)
         if (.not. all(ieee_is_finite(synthesized))) error stop 'nonfinite injected synthesis'
         max_injected_error = max(max_injected_error,maxval(abs(synthesized-field)))
         if (max_injected_error > 2.e-11_wp) error stop 'independent injected coefficient synthesis'
         cases = cases+1
      end do
      call globe%destroy()
      deallocate(field,synthesized,z,expected_a)
   end do
   if (cases /= 18) error stop 'spherical fixture count'
   print '(a)', '18 zonal harmonic fixtures: degrees 0..4 and a mixed field on three Gaussian grids.'
   print '(a,es12.4)', 'Maximum normalized-basis coefficient error: ',max_coefficient_error
   print '(a,es12.4)', 'Maximum analysis/synthesis round-trip error: ',max_round_trip_error
   print '(a,es12.4)', 'Maximum independent coefficient-injection synthesis error: ',max_injected_error
   print '(a)', 'PASS spherepack-zonal-reference'
end program zonal_reference
