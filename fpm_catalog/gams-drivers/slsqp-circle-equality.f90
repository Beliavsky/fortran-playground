! Adapted author SLSQP callback/initialization pattern; independent convex test problem.
! Modern Fortran Edition of the SLSQP Optimizer
! https://github.com/jacobwilliams/slsqp
! 
! Copyright (c) 2016-2025, Jacob Williams
! All rights reserved.
! 
! Redistribution and use in source and binary forms, with or without modification,
! are permitted provided that the following conditions are met:
! 
! * Redistributions of source code must retain the above copyright notice, this
!   list of conditions and the following disclaimer.
! 
! * Redistributions in binary form must reproduce the above copyright notice, this
!   list of conditions and the following disclaimer in the documentation and/or
!   other materials provided with the distribution.
! 
! * The names of its contributors may not be used to endorse or promote products
!   derived from this software without specific prior written permission.
! 
! THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
! ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
! WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
! DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
! ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
! (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
! LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
! ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
! (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
! SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
! 
! --------------------------------------------------------------------------------
! Original License:
! 
! SLSQP - Sequential Least Squares Programming
! Copyright (c) 1988, Dieter Kraft (kraft@hm.edu)
! Copyright (c) 1994, Association for Computing Machinery
! 
! Permission is hereby granted, free of charge, to any person obtaining a
! copy of this software and associated documentation files (the
! "Software"), to deal in the Software without restriction, including
! without limitation the rights to use, copy, modify, merge, publish,
! distribute, sublicense, and/or sell copies of the Software, and to
! permit persons to whom the Software is furnished to do so, subject to
! the following conditions:
! 
! The above copyright notice and this permission notice shall be included
! in all copies or substantial portions of the Software.
! 
! THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
! OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
! MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
! IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
! CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
! TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
! SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
module constrained_model
   use slsqp_module, only: slsqp_solver
   use slsqp_kinds, only: wp
   implicit none
   integer :: objective_calls=0,gradient_calls=0
contains
   pure subroutine model(x,f,c,g,a)
      real(wp), intent(in) :: x(:)
      real(wp), intent(out) :: f,c(:),g(:),a(:,:)
      f=(x(1)-2._wp)**2+(x(2)+1._wp)**2
      c(1)=sum(x)-1._wp ! Equality c(1)=0 comes first.
      c(2)=1._wp-sum(x*x) ! SLSQP inequalities use c>=0.
      g=2._wp*(x-[2._wp,-1._wp])
      a(1,:)=1._wp; a(2,:)=-2._wp*x
   end subroutine
   subroutine objective(me,x,f,c)
      class(slsqp_solver), intent(inout) :: me
      real(wp), intent(in) :: x(:)
      real(wp), intent(out) :: f,c(:)
      real(wp) :: g(2),a(2,2)
      objective_calls=objective_calls+1
      call model(x,f,c,g,a)
   end subroutine
   subroutine gradient(me,x,g,a)
      class(slsqp_solver), intent(inout) :: me
      real(wp), intent(in) :: x(:)
      real(wp), intent(out) :: g(:),a(:,:)
      real(wp) :: f,c(2)
      gradient_calls=gradient_calls+1
      call model(x,f,c,g,a)
   end subroutine
   subroutine check_derivatives()
      real(wp) :: x(2),plus(2),minus(2),f,c(2),g(2),a(2,2),fp,fm,cp(2),cm(2),unused_g(2),unused_a(2,2)
      real(wp), parameter :: h=1.e-6_wp
      integer :: j
      x=[0.5_wp,0.5_wp]
      call model(x,f,c,g,a)
      do j=1,2
         plus=x; minus=x; plus(j)=plus(j)+h; minus(j)=minus(j)-h
         call model(plus,fp,cp,unused_g,unused_a)
         call model(minus,fm,cm,unused_g,unused_a)
         if (abs((fp-fm)/(2*h)-g(j))>1.e-7_wp) error stop 'objective gradient check'
         if (maxval(abs((cp-cm)/(2*h)-a(:,j)))>1.e-7_wp) error stop 'constraint Jacobian check'
      end do
   end subroutine
end module
program checked_circle_equality
   use constrained_model
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
   type(slsqp_solver) :: solver
   real(wp) :: x(2),f,c(2),g(2),a(2,2),feasibility,stationarity,complementarity
   integer :: status,iterations
   logical :: initialized
   call check_derivatives()
   call solver%initialize(2,2,1,200,1.e-12_wp,objective,gradient, &
      [-2._wp,-2._wp],[2._wp,2._wp],status_ok=initialized,gradient_mode=0)
   if (.not.initialized) error stop 'SLSQP initialization'
   x=[0.5_wp,0.5_wp]
   call solver%optimize(x,status,iterations)
   if (status/=0.or..not.all(ieee_is_finite(x))) error stop 'SLSQP convergence'
   call model(x,f,c,g,a)
   if (.not.ieee_is_finite(f).or..not.all(ieee_is_finite(c))) error stop 'nonfinite objective/constraints'
   feasibility=max(abs(c(1)),max(0._wp,-c(2)),maxval(abs(x))-2._wp)
   ! Independent exact KKT multipliers: lambda=2 for the equality, mu=2>=0 for c(2)>=0.
   stationarity=maxval(abs(g-2._wp*a(1,:)-2._wp*a(2,:)))
   complementarity=abs(2._wp*c(2))
   if (max(feasibility,stationarity,complementarity)>1.e-7_wp) error stop 'independent KKT checks'
   if (maxval(abs(x-[1._wp,0._wp]))>1.e-7_wp.or.abs(f-2._wp)>1.e-7_wp) error stop 'known optimum'
   if (objective_calls<=0.or.gradient_calls<=0) error stop 'missing analytic callbacks'
   print '(a,2f18.12)', 'Computed minimizer: ',x
   print '(a,f18.12)', 'Independent objective (expected 2): ',f
   print '(a,es12.4)', 'Maximum primal constraint violation: ',feasibility
   print '(a,es12.4)', 'Stationarity with known multipliers (2,2): ',stationarity
   print '(a,es12.4)', 'Complementarity residual: ',complementarity
   print '(a,i0)', 'Objective/constraint callback calls: ',objective_calls
   print '(a,i0)', 'Gradient/Jacobian callback calls: ',gradient_calls
   print '(a,i0)', 'Iterations: ',iterations
   print '(a,i0)', 'Solver termination code: ',status
   print '(a)', 'PASS slsqp-circle-equality'
end program
