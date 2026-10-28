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
   subroutine half_life(me,x,y,EvalEvents,Value,Direction,LocEvent,LocEventAction)
      class(DiffEqSys), intent(inout) :: me
      real(wp), intent(in) :: x
      real(wp), intent(inout) :: y(:)
      integer, intent(in) :: EvalEvents(:)
      real(wp), intent(out) :: Value(:)
      integer, intent(out) :: Direction(:)
      integer, optional, intent(in) :: LocEvent
      integer(kind(FLINT_EVENTACTION_CONTINUE)), optional, intent(out) :: LocEventAction
      Value(1)=y(1)-.5_wp
      Direction(1)=-1
      if (present(LocEventAction)) LocEventAction=FLINT_EVENTACTION_TERMINATE
   end subroutine half_life
end module decay_model
program main
   use decay_model
   implicit none
   type(decay_system), target :: equation
   type(ERK_class) :: solver
   real(wp) :: finish,y(1),step
   real(wp), allocatable :: events(:,:)
   equation%n=1; equation%m=1
   equation%G=>half_life
   call solver%Init(equation,1000,ATol=[1e-11_wp],RTol=[1e-11_wp],EventsOn=.true.)
   if (solver%status/=FLINT_SUCCESS) error stop 'Initialization failed'
   finish=2._wp
   step=0._wp
   call solver%Integrate(0._wp,[1._wp],finish,y,StepSz=step,EventStates=events)
   if (solver%status/=FLINT_EVENT_TERM) error stop 'Half-life event was not found'
   if (abs(finish-log(2._wp))>1e-7_wp.or.abs(y(1)-.5_wp)>1e-7_wp) error stop
   print '(a,f12.8)', 'Computed half-life:',finish
   print '(a,f12.8)', 'Analytic log(2):  ',log(2._wp)
   print '(a,f12.8)', 'Value at event:   ',y(1)
   print *, 'PASS flint'
end program main
