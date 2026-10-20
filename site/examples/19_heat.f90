! Example: Numerical: one-dimensional heat diffusion
! Solve u_t = u_xx on [0,1], holding both endpoints at zero.
! Try changing steps or the initial profile; keep r <= 0.5 for stability.
program heat_diffusion
   use, intrinsic :: iso_fortran_env, only: real64
   implicit none
   integer, parameter :: n = 8, steps = 10
   real(real64), parameter :: r = 0.25_real64 ! r = dt/dx**2
   real(real64) :: u(0:n), next(0:n), pi, dx, dt
   integer :: i, step
   pi = acos(-1.0_real64)
   dx = 1.0_real64/n
   dt = r*dx**2
   u = [(sin(pi*i*dx), i=0,n)]
   u(0) = 0
   u(n) = 0
   do step = 1, steps
      next = u
      next(1:n-1) = u(1:n-1) + r*(u(0:n-2)-2*u(1:n-1)+u(2:n))
      u = next
   end do
   print '(a,f14.10)', 'Elapsed time: ', steps*dt
   print '(a,f14.10)', 'Center temperature: ', u(n/2)
   print '(a,f14.10)', 'Exact PDE center temperature: ', exp(-pi*pi*steps*dt)
   print '(a,2(f14.10,1x))', 'Boundary temperatures: ', u(0), u(n)
end program heat_diffusion
