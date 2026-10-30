! Adapted from the author scalar solver example; retained MIT license.
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
module root_equations
   use iso_fortran_env, only: wp=>real64
   implicit none
   integer :: problem=1, calls=0, derivative_calls=0
contains
   function value(x) result(y)
      real(wp), intent(in) :: x
      real(wp) :: y
      if (problem==1) then
         y=sin(x)/x
      else
         y=exp(x)-2._wp
      end if
   end function
   function equation(x,args) result(y)
      real(wp), intent(in) :: x
      class(*), optional, intent(inout) :: args
      real(wp) :: y
      calls=calls+1
      y=value(x)
   end function
   function derivative(x,args) result(y)
      real(wp), intent(in) :: x
      class(*), optional, intent(inout) :: args
      real(wp) :: y
      derivative_calls=derivative_calls+1
      if (problem==1) then
         y=cos(x)/x-sin(x)/(x*x)
      else
         y=exp(x)
      end if
   end function
end module
program checked_scalar_roots
   use root_equations
   use nonlin
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
   type(newton_1var_solver) :: solver
   type(fcn1var_helper) :: objective
   type(value_pair) :: limits
   type(iteration_behavior) :: tracking
   procedure(fcn1var), pointer :: fcn
   real(wp) :: a,b,x,residual,expected,actual_error
   procedure(fcn1var), pointer :: diff
   real(wp) :: midpoint,h,estimate
   fcn=>equation
   call objective%set_fcn(fcn)
   call solver%set_fcn_tolerance(1.e-12_wp)
   call solver%set_var_tolerance(1.e-12_wp)
   call solver%set_max_fcn_evals(200)
   diff=>derivative
   call objective%set_diff(diff)
   do problem=1,2
      if (problem==1) then
         a=1.5_wp; b=5._wp
      else
         a=0._wp; b=2._wp
      end if
      calls=0; derivative_calls=0
      ! Sanity check the supplied derivative, outside the solver counters.
      midpoint=(a+b)/2._wp
      h=epsilon(1._wp)**(1._wp/3._wp)*max(1._wp,abs(midpoint))
      estimate=(value(midpoint+h)-value(midpoint-h))/(2._wp*h)
      if (abs(derivative(midpoint)-estimate)>1.e-7_wp) error stop 'analytic derivative check'
      derivative_calls=0
      limits%x1=a; limits%x2=b
      x=(a+b)/2._wp
      call solver%solve(objective,x,limits,residual,ib=tracking)
      if (.not.(tracking%converge_on_fcn.or.tracking%converge_on_chng)) error stop 'solver convergence'
      if (.not.ieee_is_finite(x).or..not.ieee_is_finite(residual)) error stop 'nonfinite root/residual'
      if (x<a.or.x>b) error stop 'root outside bracket'
      if (problem==1) then
         expected=acos(-1._wp)
         print '(a)', 'Case: sin(x)/x = 0 on [1.5,5], root pi'
      else
         expected=log(2._wp)
         print '(a)', 'Case: exp(x)-2 = 0 on [0,2], root log(2)'
      end if
      actual_error=abs(x-expected)
      if (actual_error>1.e-9_wp.or.abs(value(x))>1.e-9_wp) error stop 'independent root accuracy'
      if (abs(residual-value(x))>1.e-12_wp) error stop 'reported residual disagreement'
      if (calls<=0) error stop 'missing function evaluations'
      print '(a,es22.14)', 'Computed root: ', x
      print '(a,es12.4)', 'Actual root error: ', actual_error
      print '(a,es12.4)', 'Independent absolute residual: ', abs(value(x))
      print '(a,i0)', 'Function callback calls: ', calls
      print '(a,i0)', 'Derivative callback calls: ', derivative_calls
      if (derivative_calls<=0) error stop 'analytic derivative was not used'
   end do
   print '(a)', 'PASS nonlin-roots-newton'
end program
