! Example: Types: particles and their motion
! Try changing dt or the velocity of either particle.
program particle_motion
   use, intrinsic :: iso_fortran_env, only: real64
   implicit none
   type :: particle
      real(real64) :: position(2), velocity(2)
   end type particle
   type(particle) :: p(2)
   real(real64), parameter :: dt = 0.5_real64
   integer :: i
   p(1) = particle([0.0_real64,0.0_real64], [2.0_real64,1.0_real64])
   p(2) = particle([1.0_real64,3.0_real64], [-1.0_real64,0.0_real64])
   do i = 1, size(p)
      p(i)%position = p(i)%position + dt*p(i)%velocity
      print '(a,i0,a,2(f8.3,1x))', 'Particle ', i, ' position: ', p(i)%position
   end do
end program particle_motion
