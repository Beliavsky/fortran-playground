module ode_functions
   use dop853_module, only: dop853_class, wp => dop853_wp
   implicit none
contains
   subroutine decay(me, x, y, derivative)
      class(dop853_class), intent(inout) :: me
      real(wp), intent(in) :: x, y(:)
      real(wp), intent(out) :: derivative(:)
      derivative = -y
   end subroutine
end module
program main
   use ode_functions
   implicit none
   type(dop853_class) :: solver
   real(wp) :: x, y(1)
   integer :: status
   logical :: initialized
   x = 0.0_wp
   y = 1.0_wp
   call solver%initialize(n=1, fcn=decay, status_ok=initialized)
   if (.not. initialized) error stop 'initialization failed'
   call solver%integrate(x, y, 1.0_wp, [1.e-10_wp], [1.e-10_wp], 0, status)
   if (status < 0 .or. abs(y(1)-exp(-1.0_wp)) > 1.e-8_wp) error stop 'incorrect ODE solution'
   print *, 'y(1) for dy/dx=-y:', y
   print *, 'PASS dop853'
end program main
