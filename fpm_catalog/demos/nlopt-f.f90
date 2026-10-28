module rosenbrock_model
   use iso_fortran_env, only: real64
   implicit none
contains
   function objective(x,gradient,func_data) result(f)
      real(real64), intent(in) :: x(:)
      real(real64), optional, intent(inout) :: gradient(:)
      class(*), optional, intent(in) :: func_data
      real(real64) :: f
      f=(1._real64-x(1))**2+100._real64*(x(2)-x(1)**2)**2
      if (present(gradient)) then
         gradient(1)=2*(x(1)-1)-400*x(1)*(x(2)-x(1)**2)
         gradient(2)=200*(x(2)-x(1)**2)
      end if
   end function
end module
program main
   use nlopt_wrap
   use nlopt_enum
   use rosenbrock_model
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
   type(nlopt_opt) :: opt
   real(real64) :: x(2),minimum
   integer :: status
   call create(opt,algorithm_from_string('LD_LBFGS'),2)
   associate(f=>nlopt_func(objective))
      call opt%set_min_objective(f,status)
      if (status<0) error stop 'Cannot set objective'
      call opt%set_xtol_rel(1e-9_real64,status)
      call opt%set_maxeval(1000,status)
      x=[-1.2_real64,1._real64]
      call opt%optimize(x,minimum,status)
   end associate
   if (status<0.or..not.all(ieee_is_finite(x))) error stop 'Optimization failed'
   if (maxval(abs(x-1._real64))>1e-5_real64.or.minimum>1e-10_real64) error stop
   print '(a,2f15.10)', 'Rosenbrock minimizer:',x
   print '(a,es14.5)', 'Minimum value:',minimum
   call destroy(opt)
   print *, 'PASS nlopt-f'
end program
