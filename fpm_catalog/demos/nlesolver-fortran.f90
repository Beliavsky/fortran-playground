module example_functions
   use nlesolver_module, only: nlesolver_type, wp => nlesolver_rk
   implicit none
contains
   subroutine residual(me,x,f)
      class(nlesolver_type), intent(inout) :: me
      real(wp), intent(in) :: x(:)
      real(wp), intent(out) :: f(:)
      f = [x(1)**2-2.0_wp,x(2)-3.0_wp]
   end subroutine
   subroutine jacobian(me,x,g)
      class(nlesolver_type), intent(inout) :: me
      real(wp), intent(in) :: x(:)
      real(wp), intent(out) :: g(:,:)
      g = 0.0_wp
      g(1,1) = 2*x(1)
      g(2,2) = 1.0_wp
   end subroutine
end module example_functions

program main
   use example_functions
   implicit none
   type(nlesolver_type) :: solver
   real(wp) :: x(2)
   integer :: status
   character(:), allocatable :: message
   call solver%initialize(n=2,m=2,max_iter=50,tol=1.e-10_wp,func=residual,grad=jacobian,verbose=.false.)
   call solver%status(status,message)
   if (status /= 0) error stop 'initialization failed'
   x = [1.0_wp,0.0_wp]
   call solver%solve(x)
   call solver%status(status,message)
   if (status /= 1) error stop 'required accuracy was not achieved'
   if (maxval(abs(x-[sqrt(2.0_wp),3.0_wp])) > 1.e-8_wp) error stop 'incorrect roots'
   print *, 'Roots of x**2=2 and y=3:', x
   print *, message
   print *, 'PASS nlesolver-fortran'
end program main
