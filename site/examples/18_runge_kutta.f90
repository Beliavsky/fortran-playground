! Example: Numerical: an ODE with Runge-Kutta
! Solve dy/dt = -y, y(0)=1. Try fewer steps to see the error grow.
program runge_kutta_decay
   use, intrinsic :: iso_fortran_env, only: real64
   implicit none
   integer, parameter :: n = 10
   real(real64), parameter :: final_time = 1.0_real64
   real(real64) :: h, y, k1, k2, k3, k4, exact
   integer :: i
   h = final_time/n
   y = 1.0_real64
   do i = 1, n
      k1 = -y
      k2 = -(y+h*k1/2)
      k3 = -(y+h*k2/2)
      k4 = -(y+h*k3)
      y = y + h*(k1+2*k2+2*k3+k4)/6
   end do
   exact = exp(-final_time)
   print '(a,f14.10)', 'RK4 y(1): ', y
   print '(a,f14.10)', 'Exact y(1): ', exact
   print '(a,es14.6)', 'Absolute error: ', abs(y-exact)
end program runge_kutta_decay
