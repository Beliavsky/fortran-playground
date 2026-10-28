module demo_nonlin_equations
   use iso_fortran_env, only: real64
   implicit none
contains
   subroutine equations(x, f, args)
      real(real64), intent(in) :: x(:)
      real(real64), intent(out) :: f(:)
      class(*), intent(inout), optional :: args
      ! A circle and a line intersect at (2,1) and (-1,-2).
      f(1) = x(1)**2 + x(2)**2 - 5._real64
      f(2) = x(1) - x(2) - 1._real64
   end subroutine equations
end module demo_nonlin_equations

program demo_nonlin
   use nonlin, only: vecfcn_helper, vecfcn, newton_solver, iteration_behavior
   use demo_nonlin_equations, only: equations, real64
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   type(vecfcn_helper) :: objective
   type(newton_solver) :: solver
   type(iteration_behavior) :: tracking
   procedure(vecfcn), pointer :: callback
   real(real64) :: x(2), residual(2), checked(2)

   callback => equations
   call objective%set_fcn(callback, 2, 2)
   call solver%set_max_fcn_evals(200)
   call solver%set_fcn_tolerance(1.e-10_real64)
   call solver%set_var_tolerance(1.e-10_real64)
   x = [1.8_real64, 0.8_real64]
   call solver%solve(objective, x, residual, tracking)
   call equations(x, checked)
   if (.not. all(ieee_is_finite(x)) .or. .not. all(ieee_is_finite(checked))) &
      error stop 'Nonfinite nonlinear solution'
   if (maxval(abs(checked)) > 1.e-8_real64) error stop 'Nonlinear residual check failed'
   if (maxval(abs(x-[2._real64, 1._real64])) > 1.e-8_real64) error stop 'Unexpected solution'
   print '(a,2f14.9)', 'Solution:', x
   print '(a,2es14.4)', 'Residuals:', checked
   print '(a,i0)', 'Iterations: ', tracking%iter_count
   print *, 'PASS nonlin'
end program demo_nonlin
