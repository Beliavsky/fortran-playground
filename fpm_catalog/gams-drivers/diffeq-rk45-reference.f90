! Independent API consumer; MIT: licenses/regrid-rk45-drivers-MIT.txt.
module reference_models
   use iso_fortran_env,only:wp=>real64
   implicit none
   type model_parameters
      integer::family=0,calls=0
      real(wp)::rate=1
   end type
contains
   function exact(t,family,rate) result(y)
      real(wp),intent(in)::t,rate
      integer,intent(in)::family
      real(wp)::y(2),s
      s=rate*t
      select case(family)
      case(1)
         y=[exp(s),2*exp(-s)]
      case(2)
         y=[1+s+s*s,2-s+0.5_wp*s**3]
      case(3)
         y=[cos(s)+0.25_wp*sin(s),-sin(s)+0.25_wp*cos(s)]
      case default
         error stop 'unknown reference family'
      end select
   end function
   subroutine rhs(t,y,dydt,args)
      real(wp),intent(in)::t,y(:)
      real(wp),intent(out)::dydt(:)
      class(*),optional,intent(inout)::args
      real(wp)::s
      if (.not.present(args)) error stop 'missing callback state'
      select type(args)
      type is(model_parameters)
         args%calls=args%calls+1
         s=args%rate*t
         select case(args%family)
         case(1)
            dydt=args%rate*[y(1),-y(2)]
         case(2)
            dydt=args%rate*[1+2*s,-1+1.5_wp*s*s]
         case(3)
            dydt=args%rate*[y(2),-y(1)]
         case default
            error stop 'unknown callback family'
         end select
      class default
         error stop 'incorrect callback state'
      end select
   end subroutine
end module

program main
   use reference_models
   use diffeq,only:runge_kutta_45,ode_container
   use ieee_arithmetic,only:ieee_is_finite
   implicit none
   real(wp),parameter::rates(*)=[0.5_wp,2.0_wp],tolerances(*)=[1e-8_wp,1e-10_wp]
   type(runge_kutta_45)::solver
   type(ode_container)::model
   type(model_parameters)::parameters
   real(wp),allocatable::solution(:,:)
   real(wp)::times(17),saved_times(17),iv(2),saved_iv(2),reference(2),tol,error,worst,invariant
   integer::family,ir,it,direction,i,runs,points,rhs_calls
   runs=0; points=0; rhs_calls=0; worst=0
   model%fcn=>rhs
   do family=1,3
      do ir=1,size(rates)
         do direction=1,2
            do it=1,size(tolerances)
               tol=tolerances(it)
               times=[(real(i-1,wp)/8,i=1,17)]
               if (direction==2) times=times(17:1:-1)
               parameters=model_parameters(family,0,rates(ir))
               iv=exact(times(1),family,rates(ir)); saved_iv=iv; saved_times=times
               call solver%clear_buffer()
               call solver%set_absolute_tolerance(tol)
               call solver%set_relative_tolerance(tol)
               call solver%set_maximum_step_size(0.3_wp)
               call solver%solve(model,times,iv,args=parameters)
               solution=solver%get_solution()
               if (any(shape(solution)/=[17,3])) error stop 'requested output shape'
               if (.not.all(ieee_is_finite(solution))) error stop 'nonfinite solution'
               if (maxval(abs(solution(:,1)-times))>1e-13_wp) error stop 'incomplete requested times'
               if (any(times/=saved_times).or.any(iv/=saved_iv)) error stop 'changed inputs'
               if (parameters%calls<=0) error stop 'callback not evaluated'
               if (parameters%family/=family.or.parameters%rate/=rates(ir)) error stop 'changed model state'
               do i=1,17
                  reference=exact(times(i),family,rates(ir))
                  error=maxval(abs(solution(i,2:3)-reference))/max(1.0_wp,maxval(abs(reference)))
                  if (error>50*tol) error stop 'analytical IVP reference'
                  worst=max(worst,error)
                  if (family==3) then
                     invariant=abs(sum(solution(i,2:3)**2)-1.0625_wp)
                     if (invariant>100*tol) error stop 'oscillator energy'
                  end if
                  points=points+1
               end do
               rhs_calls=rhs_calls+parameters%calls
               runs=runs+1
            end do
         end do
      end do
   end do
   if (runs/=24.or.points/=408) error stop 'accounting'
   print '(a,i0,a,i0)', 'Analytical IVP runs: ',runs,'; requested solution points: ',points
   print '(a,i0)', 'RHS callback evaluations: ',rhs_calls
   print '(a)', 'Exponential/polynomial/oscillator; two rates, both directions and two tolerances.'
   print '(a,es12.4)', 'Maximum normalized solution error: ',worst
   print '(a)', 'PASS diffeq-rk45-reference'
end program
