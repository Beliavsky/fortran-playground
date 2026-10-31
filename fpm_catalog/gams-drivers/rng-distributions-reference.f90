! Independent API consumer; MIT: licenses/raster-distributions-drivers-MIT.txt.
program distributions_reference
   use, intrinsic :: iso_fortran_env, only: dp => real64,int64
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   use m_random, only: rng_t
   implicit none
   integer, parameter :: n=20000,geometry_n=1000
   integer(int64), parameter :: seeds(2,3) = reshape([123456789_int64,987654321_int64, &
      13579_int64,24680_int64,112233_int64,998877_int64],[2,3])
   real(dp), parameter :: rates(*) = [.5_dp,2._dp,8._dp],radii(*) = [.25_dp,1._dp,3._dp]
   integer :: run
   do run = 1,3
      call moments(seeds(:,run),rates(run))
      call geometry(seeds(:,run),radii(run))
   end do
   print '(a)', '60000 normal and 60000 Poisson samples, each replayed exactly with fresh seeded objects.'
   print '(a)', '3000 circle and 3000 sphere samples: exact replay, analytic norms and broad coordinate moments.'
   print '(a)', 'Fixed-seed smoke checks do not certify statistical quality or cryptographic safety.'
   print '(a)', 'PASS rng-distributions-reference'
contains
   subroutine moments(seed,lambda)
      integer(int64), intent(in) :: seed(2)
      real(dp), intent(in) :: lambda
      type(rng_t), allocatable :: normal_rng,normal_replay,poisson_rng,poisson_replay
      real(dp) :: z,mean_z,second_z,mean_p,centered_p,zero_mass
      integer :: i,p,zeros
      ! Fresh allocations avoid the known cached-normal reseeding behavior at this pin.
      allocate(normal_rng,normal_replay,poisson_rng,poisson_replay)
      call normal_rng%set_seed(seed)
      call normal_replay%set_seed(seed)
      call poisson_rng%set_seed(seed)
      call poisson_replay%set_seed(seed)
      mean_z = 0._dp
      second_z = 0._dp
      mean_p = 0._dp
      centered_p = 0._dp
      zeros = 0
      do i = 1,n
         z = normal_rng%normal()
         if (.not. ieee_is_finite(z)) error stop 'nonfinite normal'
         if (z /= normal_replay%normal()) error stop 'normal fresh-object replay'
         mean_z = mean_z+z
         second_z = second_z+z*z
         p = poisson_rng%poisson(lambda)
         if (p < 0) error stop 'negative Poisson count'
         if (p /= poisson_replay%poisson(lambda)) error stop 'Poisson fresh-object replay'
         mean_p = mean_p+real(p,dp)
         centered_p = centered_p+(real(p,dp)-lambda)**2
         if (p == 0) zeros = zeros+1
      end do
      mean_z = mean_z/n
      second_z = second_z/n
      mean_p = mean_p/n
      centered_p = centered_p/n
      zero_mass = real(zeros,dp)/n
      if (.not. all(ieee_is_finite([mean_z,second_z,mean_p,centered_p]))) error stop 'nonfinite moments'
      if (abs(mean_z) > .04_dp .or. abs(second_z-1) > .08_dp) error stop 'normal analytic moments'
      if (abs(mean_p-lambda) > .04_dp*max(1._dp,lambda)) error stop 'Poisson analytic mean'
      if (abs(centered_p-lambda) > .12_dp*max(1._dp,lambda)) error stop 'Poisson centered moment'
      if (abs(zero_mass-exp(-lambda)) > .02_dp) error stop 'Poisson analytic zero probability'
      print '(a,f5.2,a,2f10.5)', 'Rate=',lambda,' normal mean/second moment=',mean_z,second_z
      print '(a,3f10.5)', 'Poisson mean/centered moment/zero mass=',mean_p,centered_p,zero_mass
      deallocate(normal_rng,normal_replay,poisson_rng,poisson_replay)
   end subroutine moments
   subroutine geometry(seed,radius)
      integer(int64), intent(in) :: seed(2)
      real(dp), intent(in) :: radius
      type(rng_t), allocatable :: generator,replay
      real(dp) :: xy(2),xyz(3),again2(2),again3(3),mean2(2),mean3(3),second2(2),second3(3),norm_error
      integer :: i
      allocate(generator,replay)
      call generator%set_seed(seed)
      call replay%set_seed(seed)
      mean2 = 0._dp
      mean3 = 0._dp
      second2 = 0._dp
      second3 = 0._dp
      norm_error = 0._dp
      do i = 1,geometry_n
         xy = generator%circle(radius)
         xyz = generator%sphere(radius)
         again2 = replay%circle(radius)
         again3 = replay%sphere(radius)
         if (.not. all(ieee_is_finite(xy)) .or. .not. all(ieee_is_finite(xyz))) error stop 'nonfinite geometry'
         if (any(xy /= again2) .or. any(xyz /= again3)) error stop 'geometric fresh-object replay'
         xy = xy/radius
         xyz = xyz/radius
         norm_error = max(norm_error,abs(sum(xy*xy)-1),abs(sum(xyz*xyz)-1))
         mean2 = mean2+xy
         mean3 = mean3+xyz
         second2 = second2+xy*xy
         second3 = second3+xyz*xyz
      end do
      if (norm_error > 2.e-12_dp) error stop 'analytic circle/sphere radius'
      if (maxval(abs(mean2/geometry_n)) > .15_dp .or. maxval(abs(mean3/geometry_n)) > .15_dp) &
         error stop 'geometric coordinate means'
      if (maxval(abs(second2/geometry_n-.5_dp)) > .12_dp &
         .or. maxval(abs(second3/geometry_n-1._dp/3)) > .12_dp) error stop 'geometric coordinate moments'
      print '(a,f5.2,a,es12.4)', 'Radius=',radius,' maximum normalized norm error=',norm_error
      deallocate(generator,replay)
   end subroutine geometry
end program distributions_reference
