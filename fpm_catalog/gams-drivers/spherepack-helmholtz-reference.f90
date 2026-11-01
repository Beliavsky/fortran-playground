! Independent MIT API consumer; see licenses/helmholtz-streams-drivers-MIT.txt.
program helmholtz_reference
   use spherepack, only: Sphere,GaussianSphere,RegularSphere,wp
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   class(Sphere), allocatable :: globe
   integer, parameter :: nlat_values(*)=[9,13,17],nlon_values(*)=[16,24,32]
   real(wp), parameter :: shifts(*)=[0._wp,0.25_wp,1._wp,3.5_wp]
   real(wp), allocatable :: modes(:,:,:),rhs(:,:),answer(:,:),expected(:,:)
   real(wp) :: x,y,z,amplitudes(10),lambda,error,max_error
   integer, parameter :: degrees(*)=[0,1,1,1,2,2,2,2,2,3]
   integer :: grid,kind,fixture,shift,i,j,k,nlat,nlon,cases,entries
   max_error=0; cases=0; entries=0
   do kind=1,2
      do grid=1,size(nlat_values)
         nlat=nlat_values(grid); nlon=nlon_values(grid)
         if (kind==1) then
            allocate(GaussianSphere :: globe)
         else
            allocate(RegularSphere :: globe)
         end if
         select type(globe)
         type is (GaussianSphere)
            globe=GaussianSphere(nlat,nlon)
         type is (RegularSphere)
            globe=RegularSphere(nlat,nlon)
         end select
         allocate(modes(nlat,nlon,10),rhs(nlat,nlon),answer(nlat,nlon),expected(nlat,nlon))
         do j=1,nlon
            do i=1,nlat
               x=globe%unit_vectors%radial(i,j)%x
               y=globe%unit_vectors%radial(i,j)%y
               z=globe%unit_vectors%radial(i,j)%z
               ! Restrictions of homogeneous harmonic polynomials have eigenvalue -l*(l+1).
               modes(i,j,:)=[1._wp,x,y,z,x*y,x*z,y*z,(3*z*z-1)/2,x*x-y*y,(5*z**3-3*z)/2]
            end do
         end do
         do shift=1,size(shifts)
            lambda=shifts(shift)
            do fixture=1,11
               amplitudes=0
               if (fixture<=10) then
                  amplitudes(fixture)=1
               else
                  amplitudes=[1._wp,-.5_wp,.25_wp,.75_wp,-1._wp,.5_wp,-.25_wp,.125_wp,.625_wp,-.375_wp]
               end if
               ! Poisson requires a zero mean; choose the zero-constant gauge.
               if (lambda==0) amplitudes(1)=0
               if (fixture==1 .and. lambda==0) cycle
               rhs=0; expected=0
               do k=1,10
                  expected=expected+amplitudes(k)*modes(:,:,k)
                  rhs=rhs-(real(degrees(k)*(degrees(k)+1),wp)+lambda)*amplitudes(k)*modes(:,:,k)
               end do
               call globe%invert_helmholtz(lambda,rhs,answer)
               if (.not.all(ieee_is_finite(answer))) error stop 'nonfinite Helmholtz solution'
               error=maxval(abs(answer-expected))/(1+maxval(abs(expected)))
               if (error>2.e-11_wp) error stop 'spherical harmonic PDE reference differs'
               max_error=max(max_error,error); cases=cases+1; entries=entries+nlat*nlon
            end do
         end do
         call globe%destroy()
         deallocate(globe,modes,rhs,answer,expected)
      end do
   end do
   if (cases/=258 .or. entries/=86000) error stop 'Helmholtz fixture count'
   print '(a,i0,a,i0)', 'Helmholtz/Poisson solves: ',cases,'; grid-point references: ',entries
   print '(a,es14.5)', 'Maximum normalized analytic solution error: ',max_error
   print '(a)', 'Gaussian/regular grids; zonal/nonzonal harmonics through degree 3; four nonnegative shifts.'
   print '(a)', 'Zero-shift solutions use a zero-constant gauge; resonant shifts and vector PDEs unverified.'
   print '(a)', 'PASS spherepack-helmholtz-reference'
end program
