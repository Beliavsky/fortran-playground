module example_functions
   use rklib_module, only: rk_class, wp => rk_module_rk
   implicit none
contains
   subroutine decay(me,t,y,dy)
      class(rk_class), intent(inout) :: me
      real(wp), intent(in) :: t, y(:)
      real(wp), intent(out) :: dy(:)
      dy = -y
   end subroutine decay
end module example_functions

program main
   use example_functions, only: decay
   use rklib_module, only: rk4_class, wp => rk_module_rk
   implicit none
   type(rk4_class) :: solver
   real(wp) :: value(1)
   call solver%initialize(n=1,f=decay)
   call solver%integrate(0.0_wp,[1.0_wp],0.01_wp,1.0_wp,value)
   if (abs(value(1)-exp(-1.0_wp)) > 1.e-8_wp) error stop 'incorrect RK4 result'
   print *, 'dy/dt=-y at t=1, using RK4:', value
   print *, 'PASS rklib'
end program main
