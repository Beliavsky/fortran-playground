! Adapted from Jason Christopherson's nonlin examples (MIT).
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
   function objective(x, args) result(f)
      real(real64), intent(in) :: x(:)
      class(*), optional, intent(inout) :: args
      real(real64) :: f
      objective_calls=objective_calls+1
      f=(1._real64-x(1))**2+100._real64*(x(2)-x(1)**2)**2
   end function
end module
program compare_rosenbrock
   use rosenbrock_model
   use nonlin, only: nelder_mead, fcnnvar_helper, fcnnvar, iteration_behavior
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
   type(nelder_mead) :: solver
   type(fcnnvar_helper) :: obj
   procedure(fcnnvar), pointer :: fcn
   type(iteration_behavior) :: ib
   real(real64) :: x(2), reported, independent, error
   fcn=>objective
   call obj%set_fcn(fcn,2)
   call solver%set_max_fcn_evals(5000)
   call solver%set_tolerance(1.e-12_real64)
   x=[-1.2_real64,1._real64]
   call solver%solve(obj,x,reported,ib)
   if (.not.all(ieee_is_finite(x)).or..not.ieee_is_finite(reported)) error stop 'nonfinite result'
   independent=(1._real64-x(1))**2+100._real64*(x(2)-x(1)**2)**2
   error=maxval(abs(x-1._real64))
   if (error>1.e-4_real64.or.independent>1.e-10_real64) error stop 'Rosenbrock accuracy'
   if (abs(reported-independent)>1.e-10_real64) error stop 'reported objective mismatch'
   print '(a)', 'GAMS G1b1a: Rosenbrock, nonlin nelder_mead; start (-1.2,1).'
   print '(a,2f16.10)', 'Computed minimizer: ', x
   print '(a,es12.4)', 'Maximum parameter error: ', error
   print '(a,es12.4)', 'Independent objective: ', independent
   print '(a,i0)', 'Objective callback calls: ', objective_calls
   print '(a,i0)', 'Gradient callback calls: ', gradient_calls
   print '(a,i0)', 'Solver iterations: ', ib%iter_count
   print '(a)', 'PASS nonlin-rosenbrock-nm'
end program
