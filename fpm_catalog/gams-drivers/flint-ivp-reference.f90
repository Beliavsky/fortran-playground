! Independent API consumer; see licenses/adaptive-ad-drivers-MIT.txt.
module analytic_ode_systems
   use FLINT, wp=>FLINT_WP
   implicit none
   type, extends(DiffEqSys) :: analytic_system
      integer :: family=1
      real(wp) :: parameter=1
   contains
      procedure :: F=>rhs
   end type analytic_system
contains
   function rhs(me,x,y,params) result(dy)
      class(analytic_system), intent(inout) :: me
      real(wp), intent(in) :: x,y(me%n)
      real(wp), optional, intent(in) :: params(:)
      real(wp) :: dy(size(y)),a
      a=me%parameter
      select case(me%family)
      case(1)
         dy=a*[-0.5_wp,0.25_wp,-1.5_wp]*y
      case(2)
         dy=[a*y(2),-a*y(1),3*x*x-2]
      case(3)
         dy=[-a*y(1),y(1)-a*y(2),2*y(2)-a*y(3)]
      end select
   end function rhs
   function exact(family,a,t) result(y)
      integer, intent(in) :: family
      real(wp), intent(in) :: a,t
      real(wp) :: y(3)
      select case(family)
      case(1)
         y=[1.0_wp,-2.0_wp,0.5_wp]*exp(a*[-0.5_wp,0.25_wp,-1.5_wp]*t)
      case(2)
         y=[cos(a*t)+0.25_wp*sin(a*t),-sin(a*t)+0.25_wp*cos(a*t),t**3-2*t+1]
      case(3)
         y=[1.0_wp,t,t*t]*exp(-a*t)
      end select
   end function exact
end module analytic_ode_systems
program checked_flint
   use analytic_ode_systems
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer, parameter :: methods(4)=[ERK_DOP853,ERK_DOP54,ERK_VERNER98R,ERK_VERNER65E]
   integer :: im,family,parameter,direction,offset,solves=0,dense_entries=0,endpoint_entries=0
   real(wp) :: worst=0
   do im=1,4
      do family=1,3
         do parameter=1,2
            do direction=-1,1,2
               do offset=1,2
                  call fixture(methods(im),family,parameter,direction,offset)
               end do
            end do
         end do
      end do
   end do
   print '(a,i0)', 'Adaptive integrations: ',solves
   print '(a,i0)', 'Endpoint reference entries: ',endpoint_entries
   print '(a,i0)', 'Dense-output reference entries: ',dense_entries
   print '(a,es12.4)', 'Maximum normalized error: ',worst
   print '(a)', 'PASS flint-ivp-reference'
contains
   subroutine fixture(method,family,parameter,direction,offset)
      integer, intent(in) :: method,family,parameter,direction,offset
      type(analytic_system), target :: equation
      type(ERK_class) :: solver
      real(wp) :: a,t0,requested,finish,step,y0(3),saved(3),y(3),times(17),values(3,17),again(3,17)
      integer :: j
      equation%n=3; equation%m=0; equation%family=family
      a=0.5_wp
      if (parameter==2) a=1.5_wp
      equation%parameter=a
      t0=-0.5_wp
      if (offset==2) t0=0.75_wp
      requested=t0+direction*1.25_wp
      finish=requested; y0=exact(family,a,t0); saved=y0; step=0
      if (parameter==1) then
         call solver%Init(equation,10000,Method=method,ATol=[1e-12_wp],RTol=[1e-11_wp],InterpOn=.true.)
      else
         call solver%Init(equation,10000,Method=method, &
            ATol=[1e-12_wp,2e-12_wp,4e-12_wp],RTol=[1e-11_wp,2e-11_wp,4e-11_wp],InterpOn=.true.)
      end if
      if (solver%status/=FLINT_SUCCESS) error stop 'initialization status'
      call solver%Integrate(t0,y0,finish,y,StepSz=step)
      if (solver%status/=FLINT_SUCCESS) error stop 'integration status'
      if (.not.ieee_is_finite(finish)) error stop 'nonfinite reached time'
      if (abs(finish-requested)>32*epsilon(t0)*max(1.0_wp,abs(requested))) error stop 'endpoint not reached'
      if (any(y0/=saved)) error stop 'initial state modified'
      call compare(y,exact(family,a,requested))
      endpoint_entries=endpoint_entries+3
      times=[(t0+(requested-t0)*real(j-1,wp)/16,j=1,17)]
      call solver%Interpolate(times,values,SaveInterpCoeffs=.true.)
      if (solver%status/=FLINT_SUCCESS) error stop 'first dense-output status'
      call solver%Interpolate(times,again,SaveInterpCoeffs=.false.)
      if (solver%status/=FLINT_SUCCESS) error stop 'repeat dense-output status'
      do j=1,17
         call compare(values(:,j),exact(family,a,times(j)))
         call compare(again(:,j),exact(family,a,times(j)))
      end do
      if (any(values/=again)) error stop 'repeated interpolation changed'
      dense_entries=dense_entries+2*3*17; solves=solves+1
   end subroutine fixture
   subroutine compare(y,reference)
      real(wp), intent(in) :: y(3),reference(3)
      real(wp) :: error
      if (.not.all(ieee_is_finite(y))) error stop 'nonfinite solution'
      error=maxval(abs(y-reference)/(1+abs(reference)))
      worst=max(worst,error)
      if (error>5e-9_wp) error stop 'closed-form solution mismatch'
   end subroutine compare
end program checked_flint
