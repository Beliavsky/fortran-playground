module oscillator_model
   use iso_fortran_env, only: dp => real64
   implicit none
contains
   subroutine rhs(t,y,dydt,args)
      real(dp), intent(in) :: t, y(:)
      real(dp), intent(out) :: dydt(:)
      class(*), optional, intent(inout) :: args
      dydt = [y(2), -y(1)-0.2_dp*y(2)]
   end subroutine
end module

program damped_oscillator
   use diffeq, only: runge_kutta_45, ode_container
   use oscillator_model, only: dp, rhs
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   type(runge_kutta_45) :: solver
   type(ode_container) :: model
   real(dp), allocatable :: solution(:,:), exact(:)
   real(dp) :: frequency, error
   integer :: n
   model%fcn => rhs
   call solver%set_absolute_tolerance(1.e-10_dp)
   call solver%set_relative_tolerance(1.e-10_dp)
   call solver%solve(model,[0.0_dp,10.0_dp],[1.0_dp,0.0_dp])
   solution = solver%get_solution()
   n = size(solution,1)
   if (n<2) error stop 'No solution'
   if (.not. all(ieee_is_finite(solution))) error stop 'Nonfinite solution'
   if (abs(solution(n,1)-10.0_dp)>1.e-9_dp) error stop 'Incomplete integration'
   frequency = sqrt(0.99_dp)
   exact = exp(-0.1_dp*solution(:,1)) * &
      (cos(frequency*solution(:,1))+0.1_dp/frequency*sin(frequency*solution(:,1)))
   error = maxval(abs(solution(:,2)-exact))
   print '(a,i0)', 'Adaptive solution points: ', n
   print '(a,f12.8)', 'Displacement at time 10: ', solution(n,2)
   print '(a,es12.4)', 'Maximum error against analytic solution: ', error
   if (error>1.e-7_dp) error stop 'Oscillator check'
   print *, 'PASS diffeq'
end program
