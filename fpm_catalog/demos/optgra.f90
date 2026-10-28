module playground_optgra_functions
   use optgra_module, only: optgra,wp => optgra_wp
   implicit none
contains
   subroutine values(me,x,c,i)
      class(optgra), intent(inout) :: me
      real(wp), intent(in) :: x(:)
      real(wp), intent(out) :: c(:)
      integer, intent(in) :: i
      c(1) = sum(x)-3.0_wp
      c(2) = sum((x-1.0_wp)**2)
   end subroutine
   subroutine derivatives(me,x,c,jac)
      class(optgra), intent(inout) :: me
      real(wp), intent(in) :: x(:)
      real(wp), intent(out) :: c(:),jac(:,:)
      call values(me,x,c,0)
      jac(1,:) = 1
      jac(2,:) = 2*(x-1.0_wp)
   end subroutine
end module

program demo_optgra
   use playground_optgra_functions
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   type(optgra) :: solver
   real(wp) :: x(2),c(2)
   integer :: status,iterations,units(3),i
   character(len=80), parameter :: cnames(2)=[character(len=80) :: 'x+y-3','objective']
   character(len=80), parameter :: xnames(2)=[character(len=80) :: 'x','y']
   do i=1,3
      open(newunit=units(i),status='scratch',action='readwrite')
   end do
   ! Consca specifies convergence thresholds, not unit scale factors.
   call solver%initialize(2,1,values,derivatives,[1e-4_wp,1e-4_wp],[1,1],[1e-7_wp,1e-9_wp], &
      cnames,[5,9],[1,-1],1,[1e-5_wp,1e-5_wp],1.0_wp,1.0_wp,100,10,10,10,10, &
      units(1),0,0,[1.0_wp,1.0_wp],xnames,[1,1],[0,0],units(2),0,0,units(3),0,2)
   x = [0.0_wp,0.0_wp]
   call solver%solve(x,c,status,iterations)
   print '(a,i0)', 'Solver termination: ',status
   if (.not. all(ieee_is_finite(x))) error stop 'Nonfinite optimum'
   if (status /= 1) error stop 'Solver did not report a feasible optimum'
   if (maxval(abs(x-1.5_wp))>1e-5_wp) error stop 'Known optimum differs'
   if (sum(x)<3.0_wp-1e-7_wp) error stop 'Constraint violated'
   if (abs(sum((x-1.0_wp)**2)-0.5_wp)>1e-5_wp) error stop 'Wrong objective'
   print '(a)', 'Minimize (x-1)**2+(y-1)**2 subject to x+y >= 3.'
   print '(a,2f14.8)', 'Optimal x,y: ',x
   print '(a,f14.8)', 'Objective:   ',sum((x-1.0_wp)**2)
   print '(a,es12.3)', 'Constraint violation: ',max(0.0_wp,3.0_wp-sum(x))
   call solver%destroy()
   do i=1,3
      close(units(i))
   end do
   print '(a)', 'PASS optgra'
end program
