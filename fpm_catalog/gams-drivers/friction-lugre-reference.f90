! Independent MIT API consumer; see licenses/friction-torch-drivers-MIT.txt.
module lugre_reference_system
   use, intrinsic :: iso_fortran_env, only: real64
   use friction, only: lugre_model
   implicit none
   type :: segment_parameters
      type(lugre_model) :: friction
      real(real64) :: velocity,load
      integer :: calls=0
   end type
contains
   subroutine rhs(t,z,dz,args)
      real(real64), intent(in) :: t,z(:)
      real(real64), intent(out) :: dz(:)
      class(*), intent(inout), optional :: args
      if (.not.present(args)) error stop 'missing segment parameters'
      select type(args)
      type is (segment_parameters)
         call args%friction%state(t,0.0_real64,args%velocity,args%load,z,dz)
         args%calls=args%calls+1
      class default
         error stop 'wrong segment parameter type'
      end select
   end subroutine
end module

program lugre_ivp_reference
   use lugre_reference_system
   use diffeq, only: runge_kutta_23,ode_container
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   real(real64), parameter :: loads(*)=[2.0_real64,5.0_real64,11.0_real64]
   real(real64), parameter :: velocities(*)=[0.125_real64,-0.25_real64,0.0_real64,0.0625_real64]
   real(real64), parameter :: durations(*)=[0.25_real64,0.125_real64,0.375_real64,0.5_real64]
   type(segment_parameters) :: p
   type(ode_container) :: system
   type(runge_kutta_23) :: solver
   real(real64), allocatable :: solution(:,:)
   real(real64) :: times(5),z(1),start,exact_start,g,rate,equilibrium,reference,derivative,force,dz(1)
   real(real64) :: state_error,derivative_error,force_error,max_state,max_derivative,max_force
   integer :: parameters,load_case,initial,orientation,segment,i,runs,points,calls
   runs=0; points=0; calls=0; max_state=0; max_derivative=0; max_force=0
   system%fcn=>rhs
   do parameters=1,4
      p%friction%static_coefficient=0.5_real64+parameters/16.0_real64
      p%friction%coulomb_coefficient=0.25_real64+parameters/32.0_real64
      p%friction%stribeck_velocity=0.125_real64
      p%friction%stiffness=8.0_real64+parameters
      p%friction%damping=parameters/8.0_real64
      p%friction%viscous_damping=parameters/16.0_real64
      p%friction%shape_parameter=real(parameters,real64)
      if (.not.p%friction%has_internal_state()) error stop 'missing LuGre state'
      if (p%friction%get_state_variable_count()/=1) error stop 'wrong LuGre state count'
      do load_case=1,size(loads)
         do initial=-1,1
            do orientation=1,2
               exact_start=initial/16.0_real64; z=exact_start
               do segment=1,4
                  p%velocity=velocities(segment)
                  if (orientation==2) p%velocity=-p%velocity
                  p%load=loads(load_case)*(1+real(segment-1,real64)/4)
                  p%calls=0
                  times=[(durations(segment)*real(i-1,real64)/4,i=1,5)]
                  g=p%load/p%friction%stiffness*(p%friction%coulomb_coefficient+ &
                     (p%friction%static_coefficient-p%friction%coulomb_coefficient)/ &
                     (1+(abs(p%velocity)/p%friction%stribeck_velocity)**p%friction%shape_parameter))
                  rate=abs(p%velocity)/g
                  equilibrium=0
                  if (rate>0) equilibrium=p%velocity/rate
                  start=z(1)
                  call solver%clear_buffer()
                  call solver%set_absolute_tolerance(1.e-11_real64)
                  call solver%set_relative_tolerance(1.e-11_real64)
                  call solver%set_maximum_step_size(durations(segment)/8)
                  call solver%solve(system,times,z,args=p)
                  solution=solver%get_solution()
                  if (any(shape(solution)/=[5,2])) error stop 'incomplete LuGre solution'
                  if (.not.all(ieee_is_finite(solution))) error stop 'nonfinite LuGre solution'
                  if (maxval(abs(solution(:,1)-times))>1.e-13_real64) error stop 'wrong LuGre times'
                  if (p%calls<=0 .or. z(1)/=start) error stop 'LuGre callback/input contract'
                  do i=1,5
                     reference=exact_start
                     if (rate>0) reference=equilibrium+(exact_start-equilibrium)*exp(-rate*times(i))
                     derivative=p%velocity-rate*reference
                     call p%friction%state(times(i),0.0_real64,p%velocity,p%load,[reference],dz)
                     force=p%friction%evaluate(times(i),0.0_real64,p%velocity,p%load,solution(i,2:2))
                     if (.not.all(ieee_is_finite([dz(1),force]))) error stop 'nonfinite LuGre state/force'
                     state_error=abs(solution(i,2)-reference)/(1+abs(reference))
                     derivative_error=abs(dz(1)-derivative)/(1+abs(derivative))
                     force_error=abs(force-(p%friction%stiffness*reference+p%friction%damping*derivative+ &
                        p%friction%viscous_damping*p%velocity))/(1+abs(force))
                     if (state_error>2.e-8_real64) error stop 'LuGre closed-form state reference'
                     if (derivative_error>2.e-13_real64) error stop 'LuGre state derivative reference'
                     if (force_error>2.e-7_real64) error stop 'LuGre force history reference'
                     max_state=max(max_state,state_error); max_derivative=max(max_derivative,derivative_error)
                     max_force=max(max_force,force_error); points=points+1
                  end do
                  if (rate>0) exact_start=equilibrium+(exact_start-equilibrium)*exp(-rate*times(5))
                  z=solution(5,2:2); runs=runs+1; calls=calls+p%calls
               end do
            end do
         end do
      end do
   end do
   if (runs/=288 .or. points/=1440) error stop 'LuGre reference counts'
   print '(a,i0,a,i0)', 'LuGre constant-velocity segments: ',runs,'; state/derivative/force references each: ',points
   print '(a,i0)', 'Numerical integration callback evaluations: ',calls
   print '(a,3es14.5)', 'Max normalized state, derivative and force errors: ',max_state,max_derivative,max_force
   print '(a)', '72 histories; velocity reversals, rest, changing loads and nonzero initial bristle states.'
   print '(a)', 'Public LuGre state integration only; private fitting callbacks and parameter fitting unverified.'
   print '(a)', 'PASS friction-lugre-reference'
end program
