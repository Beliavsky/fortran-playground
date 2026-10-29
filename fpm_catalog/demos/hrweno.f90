module advection_problem
   use hrweno_kinds, only: rk
   use hrweno_weno, only: weno
   implicit none
   integer, parameter :: n = 64
   real(rk), parameter :: dx = 1.0_rk/n
   type(weno) :: reconstruction
contains
   subroutine rhs(t, u, du)
      real(rk), intent(in) :: t, u(:)
      real(rk), intent(out) :: du(:)
      real(rk) :: extended(n+6), left(n+6), right(n+6), flux(0:n)
      ! Three periodic ghost cells at either end of the physical domain.
      extended(4:n+3) = u
      extended(1:3) = u(n-2:n)
      extended(n+4:n+6) = u(1:3)
      call reconstruction%reconstruct(extended, left, right)
      ! Unit positive advection speed: upwind flux is the right cell value.
      flux(0) = right(3)
      flux(1:n) = right(4:n+3)
      flux(n) = flux(0)
      du = -(flux(1:n)-flux(0:n-1))/dx
   end subroutine rhs
end module advection_problem

program periodic_advection
   use advection_problem
   use hrweno_tvdode, only: rktvd
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
   type(rktvd) :: solver
   real(rk), parameter :: pi = acos(-1.0_rk), dt = 0.002_rk
   real(rk) :: x(n), u(n), exact(n), time, factor, error, mass
   integer :: i
   x = [( (i-0.5_rk)*dx, i=1,n )]
   ! Exact cell averages, rather than point samples.
   factor = sin(pi*dx)/(pi*dx)
   u = 1 + 0.2_rk*factor*sin(2*pi*x)
   reconstruction = weno(ncells=n+6, k=3, eps=1.e-6_rk)
   solver = rktvd(rhs, n, order=3)
   time = 0
   call solver%integrate(u, time, 0.25_rk, dt)
   exact = 1 + 0.2_rk*factor*sin(2*pi*(x-time))
   error = maxval(abs(u-exact))
   mass = sum(u)*dx
   if (.not.all(ieee_is_finite(u))) error stop 'Nonfinite solution'
   if (abs(time-0.25_rk)>1.e-12_rk .or. error>1.e-4_rk) error stop 'Advection error'
   if (abs(mass-1.0_rk)>1.e-11_rk) error stop 'Mass conservation error'
   print '(a,f8.3)', 'Periodic advection time: ', time
   print '(a,es12.4)', 'Maximum cell-average error: ', error
   print '(a,f16.12)', 'Conserved mass: ', mass
   print *, 'PASS hrweno'
end program periodic_advection
