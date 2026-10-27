module example_functions
   use slsqp_module, only: slsqp_solver
   use slsqp_kinds, only: wp
   implicit none
contains
   subroutine objective(me,x,f,c)
      class(slsqp_solver), intent(inout) :: me
      real(wp), intent(in) :: x(:)
      real(wp), intent(out) :: f, c(:)
      f = sum(x*x)
      c(1) = sum(x)-1.0_wp
   end subroutine
   subroutine gradient(me,x,g,a)
      class(slsqp_solver), intent(inout) :: me
      real(wp), intent(in) :: x(:)
      real(wp), intent(out) :: g(:), a(:,:)
      g = 2*x
      a = 1.0_wp
   end subroutine
end module example_functions

program main
   use example_functions, only: objective, gradient
   use slsqp_module, only: slsqp_solver
   use slsqp_kinds, only: wp
   implicit none
   type(slsqp_solver) :: solver
   real(wp) :: x(2)
   logical :: initialized
   integer :: status
   ! Minimize x(1)**2+x(2)**2 subject to x(1)+x(2)=1.
   x = [0.2_wp,0.8_wp]
   call solver%initialize(2,1,1,100,1.e-9_wp,objective,gradient, &
      [0.0_wp,0.0_wp],[1.0_wp,1.0_wp],status_ok=initialized)
   if (.not. initialized) error stop 'initialization failed'
   call solver%optimize(x,status)
   if (status /= 0 .or. maxval(abs(x-0.5_wp)) > 1.e-6_wp) error stop 'incorrect optimum'
   print *, 'Constrained minimum at:', x
   print *, 'PASS slsqp'
end program main
