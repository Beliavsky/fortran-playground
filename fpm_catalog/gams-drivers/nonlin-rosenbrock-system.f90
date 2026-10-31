! Adapted author solver API patterns; common nonlinear system and checked root.
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
module system_equations
   use iso_fortran_env, only: wp=>real64
   implicit none
contains
   subroutine equations(x,f,args)
      real(wp), intent(in) :: x(:)
      real(wp), intent(out) :: f(:)
      class(*), optional, intent(inout) :: args
      f=[1._wp-x(1),10._wp*(x(2)-x(1)**2)]
   end subroutine
   subroutine jacobian(x,jac,args)
      real(wp), intent(in) :: x(:)
      real(wp), intent(out) :: jac(:,:)
      class(*), optional, intent(inout) :: args
      jac(1,:)=[-1._wp,0._wp]
      jac(2,:)=[-20._wp*x(1),10._wp]
   end subroutine
end module
program checked_nonlinear_system
   use system_equations
   use nonlin
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
   real(wp), parameter :: starts(2,2)=reshape([-1.2_wp,1._wp,2._wp,2._wp],[2,2])
   type(vecfcn_helper) :: problem(2)
   type(newton_solver) :: solver
   type(iteration_behavior) :: tracking
   procedure(vecfcn), pointer :: fptr
   procedure(jacobianfcn), pointer :: jptr
   real(wp) :: x(2),f(2),reference_f(2),root_error,residual
   integer :: case_number,mode
   fptr=>equations
   jptr=>jacobian
   call problem(1)%set_fcn(fptr,2,2)
   call problem(2)%set_fcn(fptr,2,2)
   call problem(2)%set_jacobian(jptr)
   call solver%set_max_fcn_evals(2000)
   call solver%set_fcn_tolerance(1.e-10_wp)
   call solver%set_var_tolerance(1.e-12_wp)
   call solver%set_gradient_tolerance(1.e-12_wp)
   call solver%set_print_status(.false.)
   do mode=1,2
      if (mode==1) then
         print '(a)', 'Finite-difference Jacobian'
      else
         print '(a)', 'Analytic Jacobian'
      end if
      do case_number=1,2
         x=starts(:,case_number)
         call solver%solve(problem(mode),x,f,tracking)
         if (.not.(tracking%converge_on_fcn.or.tracking%converge_on_chng)) error stop 'no root convergence'
         if (.not.all(ieee_is_finite(x)).or..not.all(ieee_is_finite(f))) error stop 'nonfinite solver result'
         reference_f=[1._wp-x(1),10._wp*(x(2)-x(1)**2)]
         residual=maxval(abs(reference_f))
         root_error=maxval(abs(x-1._wp))
         if (residual>1.e-8_wp.or.root_error>1.e-8_wp) error stop 'root or residual mismatch'
         if (maxval(abs(f-reference_f))>1.e-12_wp) error stop 'returned residual mismatch'
         print '(a,2f8.3,a,2f14.10)', 'Start:',starts(:,case_number),' root:',x
         print '(a,i0,a,i0,a,es10.2,a,es10.2)', 'iterations=',tracking%iter_count, &
            ' function calls=',tracking%fcn_count,' residual=',residual,' root error=',root_error
         print '(a,l1,a,l1)', 'function convergence=',tracking%converge_on_fcn, &
            ' change convergence=',tracking%converge_on_chng
      end do
   end do
   print '(a)', 'PASS nonlin-rosenbrock-system'
end program
