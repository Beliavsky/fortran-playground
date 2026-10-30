! Independent NLopt API driver; Rosenbrock model shared with the nonlin adaptations (MIT).
! MIT License
! 
! Copyright (c) 2017-2026 Jason Christopherson
! 
! Permission is hereby granted, free of charge, to any person obtaining a copy
! of this software and associated documentation files (the "Software"), to deal
! in the Software without restriction, including without limitation the rights
! to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
! copies of the Software, and to permit persons to whom the Software is
! furnished to do so, subject to the following conditions:
! 
! The above copyright notice and this permission notice shall be included in all
! copies or substantial portions of the Software.
! 
! THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
! IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
! FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
! AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
! LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
! OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
! SOFTWARE.

module rosenbrock_model
   use iso_fortran_env, only: real64
   implicit none
   integer :: objective_calls=0, gradient_calls=0
contains
   function objective(x, gradient, func_data) result(f)
      real(real64), intent(in) :: x(:)
      real(real64), optional, intent(inout) :: gradient(:)
      class(*), optional, intent(in) :: func_data
      real(real64) :: f
      objective_calls=objective_calls+1
      f=(1._real64-x(1))**2+100._real64*(x(2)-x(1)**2)**2
      if (present(gradient)) then
         gradient_calls=gradient_calls+1
         gradient(1)=2*(x(1)-1)-400*x(1)*(x(2)-x(1)**2)
         gradient(2)=200*(x(2)-x(1)**2)
      end if
   end function
   subroutine check_gradient()
      real(real64) :: x(2), plus(2), minus(2), g(2), fd(2), unused
      real(real64), parameter :: h=1.e-6_real64
      integer :: i
      x=[-1.2_real64,1._real64]
      unused=objective(x,g)
      do i=1,2
         plus=x; minus=x
         plus(i)=plus(i)+h; minus(i)=minus(i)-h
         fd(i)=(objective(plus)-objective(minus))/(2*h)
      end do
      if (maxval(abs(g-fd))>1.e-5_real64) error stop 'analytic gradient check'
      objective_calls=0; gradient_calls=0
   end subroutine
end module
program compare_rosenbrock
   use rosenbrock_model
   use nlopt_wrap
   use nlopt_enum, only: algorithm_from_string
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
   type(nlopt_opt) :: opt
   real(real64) :: x(2), reported, independent, error
   integer :: status
   call check_gradient()
   call create(opt,algorithm_from_string('LD_LBFGS'),2)
   associate(f=>nlopt_func(objective))
      call opt%set_min_objective(f,status)
      if (status<0) error stop 'set objective'
      call opt%set_xtol_rel(1.e-9_real64,status)
      if (status<0) error stop 'set variable tolerance'
      call opt%set_ftol_abs(1.e-14_real64,status)
      if (status<0) error stop 'set function tolerance'
      call opt%set_maxeval(5000,status)
      if (status<0) error stop 'set evaluation limit'
      x=[-1.2_real64,1._real64]
      call opt%optimize(x,reported,status)
   end associate
   call destroy(opt)
   if (status<0.or..not.all(ieee_is_finite(x)).or..not.ieee_is_finite(reported)) &
      error stop 'optimization failed'
   independent=(1._real64-x(1))**2+100._real64*(x(2)-x(1)**2)**2
   error=maxval(abs(x-1._real64))
   if (error>1.e-4_real64.or.independent>1.e-10_real64) error stop 'Rosenbrock accuracy'
   if (abs(reported-independent)>1.e-10_real64) error stop 'reported objective mismatch'
   print '(a)', 'GAMS G1b1b: Rosenbrock, NLopt LD_LBFGS; start (-1.2,1).'
   print '(a,2f16.10)', 'Computed minimizer: ', x
   print '(a,es12.4)', 'Maximum parameter error: ', error
   print '(a,es12.4)', 'Independent objective: ', independent
   print '(a,i0)', 'Objective callback calls: ', objective_calls
   print '(a,i0)', 'Gradient callback calls: ', gradient_calls
   print '(a,i0)', 'Solver termination code: ', status
   print '(a)', 'PASS nlopt-rosenbrock-lbfgs'
end program
