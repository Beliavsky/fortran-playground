module decay_model
   use FLINT, wp=>FLINT_WP
   implicit none
   type, extends(DiffEqSys) :: decay_system
   contains
      procedure :: F=>rhs
   end type
contains
   function rhs(me,x,y,params) result(dy)
      class(decay_system), intent(inout) :: me
      real(wp), intent(in) :: x,y(me%n)
      real(wp), optional, intent(in) :: params(:)
      real(wp) :: dy(size(y))
      dy=-y
   end function rhs
end module decay_model
program main
   use decay_model
   implicit none
   type(decay_system), target :: equation
   type(ERK_class) :: solver
   real(wp) :: finish,y(1),step,times(5),values(1,5)
   integer :: i
   equation%n=1; equation%m=0
   ! Keep the dense solution, then sample it without integrating again.
   call solver%Init(equation,1000,ATol=[1e-11_wp],RTol=[1e-11_wp],InterpOn=.true.)
   if (solver%status/=FLINT_SUCCESS) error stop 'Initialization failed'
   finish=2._wp
   step=0._wp
   call solver%Integrate(0._wp,[1._wp],finish,y,StepSz=step)
   if (solver%status/=FLINT_SUCCESS) error stop 'Integration failed'
   times=[(real(i-1,wp)*.5_wp,i=1,5)]
   call solver%Interpolate(times,values)
   if (solver%status/=FLINT_SUCCESS) error stop 'Interpolation failed'
   if (abs(y(1)-exp(-finish))>1e-9_wp) error stop
   if (maxval(abs(values(1,:)-exp(-times)))>1e-9_wp) error stop
   print '(a)', '    Time     Dense solution       exp(-t)'
   do i=1,size(times)
      print '(f8.2,2f18.12)', times(i),values(1,i),exp(-times(i))
   end do
   print *, 'PASS flint'
end program main
