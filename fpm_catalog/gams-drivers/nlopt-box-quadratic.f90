! Original checked bound-constrained quadratic example using the public NLopt API.
module box_model
   use iso_fortran_env, only: wp=>real64
   implicit none
   real(wp), parameter :: lower(2)=[0._wp,0._wp],upper(2)=[1._wp,2._wp],target(2)=[2._wp,-1._wp]
   integer :: objective_calls=0,gradient_calls=0
contains
   pure function value(x) result(f)
      real(wp), intent(in) :: x(:)
      real(wp) :: f
      f=sum((x-target)**2)
   end function
   pure function derivative(x) result(g)
      real(wp), intent(in) :: x(:)
      real(wp) :: g(size(x))
      g=2._wp*(x-target)
   end function
   subroutine check_gradient()
      real(wp) :: x(2),plus(2),minus(2),fd(2)
      real(wp), parameter :: h=1.e-6_wp
      integer :: j
      x=[0.25_wp,1._wp]
      do j=1,2
         plus=x; minus=x; plus(j)=plus(j)+h; minus(j)=minus(j)-h
         fd(j)=(value(plus)-value(minus))/(2._wp*h)
      end do
      if (maxval(abs(fd-derivative(x)))>1.e-7_wp) error stop 'analytic objective gradient'
   end subroutine
   function objective(x,gradient,func_data) result(f)
      real(wp), intent(in) :: x(:)
      real(wp), optional, intent(inout) :: gradient(:)
      class(*), optional, intent(in) :: func_data
      real(wp) :: f
      objective_calls=objective_calls+1
      f=value(x)
      if (present(gradient)) then
         gradient_calls=gradient_calls+1
         gradient=derivative(x)
      end if
   end function
end module
program checked_box_minimum
   use box_model
   use ieee_arithmetic, only: ieee_is_finite
   use nlopt_wrap
   use nlopt_enum, only: algorithm_from_string
   implicit none
   real(wp) :: x(2),reported,independent,feasibility,projected
   type(nlopt_opt) :: opt
   integer :: status
   call check_gradient()
   call create(opt,algorithm_from_string('LD_LBFGS'),2)
   associate(f=>nlopt_func(objective))
      call opt%set_min_objective(f,status)
      if (status<0) error stop 'NLopt objective setup'
      call opt%set_lower_bounds(lower,status)
      if (status<0) error stop 'NLopt lower bounds'
      call opt%set_upper_bounds(upper,status)
      if (status<0) error stop 'NLopt upper bounds'
      call opt%set_xtol_rel(1.e-10_wp,status)
      if (status<0) error stop 'NLopt x tolerance'
      call opt%set_ftol_abs(1.e-14_wp,status)
      if (status<0) error stop 'NLopt objective tolerance'
      call opt%set_maxeval(1000,status)
      if (status<0) error stop 'NLopt evaluation limit'
      x=[0.25_wp,1._wp]
      call opt%optimize(x,reported,status)
   end associate
   call destroy(opt)
   if (status<1.or.status>4) error stop 'NLopt stopped without convergence'
   if (.not.all(ieee_is_finite(x)).or..not.ieee_is_finite(reported)) error stop 'nonfinite optimum'
   independent=value(x)
   feasibility=max(0._wp,maxval(lower-x),maxval(x-upper))
   projected=maxval(abs(x-min(upper,max(lower,x-derivative(x)))))
   if (feasibility>1.e-10_wp.or.projected>1.e-8_wp) error stop 'box feasibility/stationarity'
   if (maxval(abs(x-[1._wp,0._wp]))>1.e-8_wp.or.abs(independent-2._wp)>1.e-8_wp) &
      error stop 'known box optimum'
   if (abs(reported-independent)>1.e-10_wp) error stop 'reported objective disagreement'
   if (objective_calls<=0.or.gradient_calls<=0) error stop 'missing analytic evaluations'
   print '(a,2f18.12)', 'Computed minimizer: ',x
   print '(a,f18.12)', 'Independent objective (expected 2): ',independent
   print '(a,es12.4)', 'Maximum bound violation: ',feasibility
   print '(a,es12.4)', 'Projected gradient residual: ',projected
   print '(a,i0)', 'Objective evaluations: ',objective_calls
   print '(a,i0)', 'Gradient evaluations: ',gradient_calls
   print '(a,i0)', 'Solver termination code: ',status
   print '(a)', 'PASS nlopt-box-quadratic'
end program
