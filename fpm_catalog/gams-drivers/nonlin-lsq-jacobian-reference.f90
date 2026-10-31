! Independent API consumer; MIT: licenses/jacobian-transforms-drivers-MIT.txt.
module fit_problem
   use iso_fortran_env,only:wp=>real64
   implicit none
   integer::residual_calls,jacobian_calls
   real(wp)::amplitude,exponent
contains
   subroutine model(x,f,jac)
      real(wp),intent(in)::x(2)
      real(wp),intent(out)::f(5),jac(5,2)
      real(wp)::t,v
      integer::i
      do i=1,5
         t=real(i-3,wp)/2; v=exp(x(2)*t)
         f(i)=x(1)*v-amplitude*exp(exponent*t)
         jac(i,:)=[v,x(1)*t*v]
      end do
   end subroutine model
   subroutine residual_callback(x,f,args)
      real(wp),intent(in)::x(:)
      real(wp),intent(out)::f(:)
      class(*),optional,intent(inout)::args
      real(wp)::jac(5,2)
      call model(x,f,jac)
      residual_calls=residual_calls+1
   end subroutine
   subroutine jacobian_callback(x,jac,args)
      real(wp),intent(in)::x(:)
      real(wp),intent(out)::jac(:,:)
      class(*),optional,intent(inout)::args
      real(wp)::f(5)
      call model(x,f,jac)
      jacobian_calls=jacobian_calls+1
   end subroutine
end module fit_problem
program main
   use fit_problem
   use nonlin,only:vecfcn_helper,least_squares_solver,iteration_behavior,vecfcn,jacobianfcn
   use ieee_arithmetic,only:ieee_is_finite
   implicit none
   type(vecfcn_helper)::objective_helper
   type(least_squares_solver)::solver
   type(iteration_behavior)::tracking
   procedure(vecfcn),pointer::residual_pointer
   procedure(jacobianfcn),pointer::jacobian_pointer
   real(wp),parameter::amplitudes(*)=[0.5_wp,2.0_wp],exponents(*)=[-1.0_wp,0.25_wp,1.0_wp]
   real(wp)::x(2),expected(2),f(5),jac(5,2),check_f(5),check_j(5,2),plus(5),minus(5),scratch(5,2),xp(2)
   real(wp)::step,error,worst_x,worst_j,objective,expected_objective,gradient,worst_g,value
   integer::ia,ib,start_a,start_b,runs,exact_runs,jac_entries,c
   runs=0; exact_runs=0; jac_entries=0; worst_x=0; worst_j=0; worst_g=0
   residual_pointer=>residual_callback; jacobian_pointer=>jacobian_callback
   call objective_helper%set_fcn(residual_pointer,5,2)
   call objective_helper%set_jacobian(jacobian_pointer)
   call solver%set_step_scaling_factor(1.0_wp)
   call solver%set_max_fcn_evals(2000)
   call solver%set_fcn_tolerance(1e-12_wp)
   call solver%set_var_tolerance(1e-12_wp)
   call solver%set_gradient_tolerance(1e-12_wp)
   do ia=1,size(amplitudes)
      amplitude=amplitudes(ia)
      do ib=1,size(exponents)
         exponent=exponents(ib); expected=[amplitude,exponent]
         do start_a=1,2
            do start_b=1,2
               x=[amplitude*real(2*start_a-1,wp)/2,exponent+real(2*start_b-3,wp)/2]
               call fit()
               exact_runs=exact_runs+1
            end do
         end do
      end do
   end do
   if (runs/=24.or.exact_runs/=24.or.jac_entries/=240) error stop 'fixture accounting'
   print '(a,2i5)', 'Total / exact-fit solves: ',runs,exact_runs
   print '(a,i0)', 'Analytical Jacobian entries checked by central differences at starting points: ',jac_entries
   print '(a,es12.4)', 'Maximum normalized parameter error: ',worst_x
   print '(a,es12.4)', 'Maximum normalized Jacobian finite-difference error: ',worst_j
   print '(a,es12.4)', 'Maximum absolute J-transpose-residual component: ',worst_g
   print '(a)', 'PASS nonlin-lsq-jacobian-reference'
contains
   subroutine fit()
      real(wp)::start(2)
      start=x
      call model(x,check_f,check_j)
      do c=1,2
         step=1e-5_wp*max(1.0_wp,abs(x(c)))
         xp=x; xp(c)=xp(c)+step; call model(xp,plus,scratch)
         xp=x; xp(c)=xp(c)-step; call model(xp,minus,scratch)
         error=maxval(abs((plus-minus)/(2*step)-check_j(:,c)))/max(1.0_wp,maxval(abs(check_j(:,c))))
         if (error>2e-7_wp) error stop 'user Jacobian finite-difference check'
         worst_j=max(worst_j,error); jac_entries=jac_entries+5
      end do
      residual_calls=0; jacobian_calls=0
      call solver%solve(objective_helper,x,f,tracking)
      if (.not.(tracking%converge_on_fcn.or.tracking%converge_on_chng.or.tracking%converge_on_zero_diff)) &
         error stop 'nonlin normal stopping status'
      if (residual_calls<=0.or.jacobian_calls<=0) error stop 'both callbacks required'
      if (.not.all(ieee_is_finite(x)).or..not.all(ieee_is_finite(f))) error stop 'nonfinite fit'
      call model(x,check_f,check_j)
      if (maxval(abs(check_f-f))>1e-11_wp) error stop 'returned residual consistency'
      error=maxval(abs(x-expected))/max(1.0_wp,maxval(abs(expected)))
      if (error>2e-7_wp) then
         print *, 'amplitude, exponent:',amplitude,exponent
         print *, 'start, final, expected, normalized error:',start,x,expected,error
         print *, 'convergence flags:',tracking%converge_on_fcn,tracking%converge_on_chng,tracking%converge_on_zero_diff
         error stop 'known fit parameters'
      end if
      worst_x=max(worst_x,error)
      objective=sum(f*f); expected_objective=0
      if (abs(objective-expected_objective)/max(1.0_wp,expected_objective)>1e-10_wp) &
         error stop 'known minimum residual norm'
      gradient=maxval(abs([sum(check_j(:,1)*f),sum(check_j(:,2)*f)]))
      if (gradient>1e-6_wp) error stop 'least-squares stationarity'
      worst_g=max(worst_g,gradient)
      if (maxval(abs(f))>1e-8_wp) error stop 'exact-fit residual'
      runs=runs+1
   end subroutine fit
end program main
