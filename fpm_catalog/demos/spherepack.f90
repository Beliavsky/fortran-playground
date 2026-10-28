! Spherical Helmholtz example adapted from the author's examples/helmsph.f90.
! Exact solution (1+x*y)*exp(z) on the unit sphere, lambda=1.
program demo_spherepack
   use spherepack, only: GaussianSphere, wp, ip
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer(ip), parameter :: nlat=19,nlon=36
   type(GaussianSphere) :: globe
   real(wp) :: exact(nlat,nlon), rhs(nlat,nlon), solution(nlat,nlon), x,y,z,err
   integer :: i,j
   globe = GaussianSphere(nlat,nlon)
   do j=1,nlon
      do i=1,nlat
         x = globe%unit_vectors%radial(i,j)%x
         y = globe%unit_vectors%radial(i,j)%y
         z = globe%unit_vectors%radial(i,j)%z
         exact(i,j) = (1+x*y)*exp(z)
         rhs(i,j) = -(x*y*(z*z+6*(z+1))+z*(z+2))*exp(z)
      end do
   end do
   call globe%invert_helmholtz(1._wp,rhs,solution)
   if (.not. all(ieee_is_finite(solution))) error stop 'Nonfinite spherical solution'
   err = maxval(abs(solution-exact))
   print '(a,i0,a,i0)', 'Gaussian spherical grid: ',nlat,' x ',nlon
   print '(a,es12.3)', 'Maximum Helmholtz solution error: ',err
   if (err>1e-10_wp) error stop 'Spherical Helmholtz solve inaccurate'
   call globe%destroy()
   print '(a)', 'PASS spherepack'
end program
