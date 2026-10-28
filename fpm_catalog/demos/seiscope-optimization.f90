!******************************************************************
!Copyright 2013-2016 SEISCOPE II project, All rights reserved.
!
!Redistribution and use in source and binary forms, with or
!without modification, are permitted provided that the following
!conditions are met:
!
!    *  Redistributions of source code must retain the above copyright
!       notice, this list of conditions and the following disclaimer.
!    *  Redistributions in binary form must reproduce the above
!       copyright notice, this list of conditions and the following
!       disclaimer in the documentation and/or other materials provided
!       with the distribution.
!    *  Neither the name of the SEISCOPE project nor the names of
!       its contributors may be used to endorse or promote products
!       derived from this software without specific prior written permission.
!
!Warranty Disclaimer:
!THIS SOFTWARE IS PROVIDED BY THE SEISCOPE PROJECT AND CONTRIBUTORS
!"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
!LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
!FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
!SEISCOPE PROJECT OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
!INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
!BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
!LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
!CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
!STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING
!IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
!POSSIBILITY OF SUCH DAMAGE.

! Adapted from the author's app/LBFGS/test_LBFGS.f90; adds independent checks.
program main
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   use seiscope_optimization_toolbox
   implicit none
   type(optim_type) :: optim
   real :: x(2), grad(2), cost, exact_cost, exact_grad(2)
   integer :: flag, calls

   x = [1.5, 1.5]
   call Rosenbrock(x, cost, grad)
   call set_inputs(optim, cost, 1000, conv=1.e-12, l=10, print_flag=0)
   flag = 0
   calls = 0
   do while (flag /= 2 .and. flag /= 4)
      calls = calls + 1
      if (calls > 10000) error stop 'Iteration limit'
      call LBFGS(2, x, cost, grad, optim, flag)
      if (flag == 1) call Rosenbrock(x, cost, grad)
   end do
   exact_cost = (1.-x(1))**2 + 100.*(x(2)-x(1)**2)**2
   exact_grad = [2.*(x(1)-1.)-400.*x(1)*(x(2)-x(1)**2), 200.*(x(2)-x(1)**2)]
   if (flag /= 2 .or. .not. all(ieee_is_finite(x))) error stop 'Optimizer failed'
   if (maxval(abs(x-1.)) > 2.e-4 .or. exact_cost > 1.e-8) error stop 'Wrong minimum'
   if (maxval(abs(exact_grad)) > 2.e-3) error stop 'Gradient too large'
   print '(a,2f13.8)', 'Rosenbrock minimum x = ', x
   print '(a,es12.4)', 'Objective = ', exact_cost
   print '(a,i0)', 'Iterations = ', optim%cpt_iter
   print *, 'PASS seiscope-optimization'
end program main
