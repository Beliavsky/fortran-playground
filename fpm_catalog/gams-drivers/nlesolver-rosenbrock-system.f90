! Adapted author solver API patterns; common nonlinear system and checked root.
! BSD 3-Clause License
! 
! Copyright (c) 2021-2025, Jacob Williams
! All rights reserved.
! 
! Redistribution and use in source and binary forms, with or without
! modification, are permitted provided that the following conditions are met:
! 
! 1. Redistributions of source code must retain the above copyright notice, this
!    list of conditions and the following disclaimer.
! 
! 2. Redistributions in binary form must reproduce the above copyright notice,
!    this list of conditions and the following disclaimer in the documentation
!    and/or other materials provided with the distribution.
! 
! 3. Neither the name of the copyright holder nor the names of its
!    contributors may be used to endorse or promote products derived from
!    this software without specific prior written permission.
! 
! THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
! AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
! IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
! DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
! FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
! DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
! SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
! CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
! OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
! OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
module system_equations
   use nlesolver_module, only: nlesolver_type,wp=>nlesolver_rk
   implicit none
   integer :: calls=0,jac_calls=0
contains
   subroutine equations(me,x,f)
      class(nlesolver_type), intent(inout) :: me
      real(wp), intent(in) :: x(:)
      real(wp), intent(out) :: f(:)
      calls=calls+1
      f=[1._wp-x(1),10._wp*(x(2)-x(1)**2)]
   end subroutine
   subroutine jacobian(me,x,jac)
      class(nlesolver_type), intent(inout) :: me
      real(wp), intent(in) :: x(:)
      real(wp), intent(out) :: jac(:,:)
      jac_calls=jac_calls+1
      jac(1,:)=[-1._wp,0._wp]
      jac(2,:)=[-20._wp*x(1),10._wp]
   end subroutine
end module
program checked_nonlinear_system
   use system_equations
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
   real(wp), parameter :: starts(2,2)=reshape([-1.2_wp,1._wp,2._wp,2._wp],[2,2])
   type(nlesolver_type) :: solver
   real(wp) :: x(2),f(2),root_error,residual
   integer :: case_number,status
   character(:), allocatable :: message
   do case_number=1,2
      call solver%initialize(n=2,m=2,max_iter=200,tol=1.e-10_wp,tolx=1.e-12_wp, &
         func=equations,grad=jacobian,step_mode=2,use_broyden=.false.,sparsity_mode=1,verbose=.false.)
      call solver%status(status,message)
      if (status/=0) error stop 'solver initialization failed'
      x=starts(:,case_number)
      calls=0;jac_calls=0
      call solver%solve(x)
      call solver%status(status,message)
      if (status/=1) error stop 'solver did not report required accuracy'
      if (.not.all(ieee_is_finite(x))) error stop 'nonfinite root'
      ! Recompute the original equations independently of solver termination.
      f=[1._wp-x(1),10._wp*(x(2)-x(1)**2)]
      if (.not.all(ieee_is_finite(f))) error stop 'nonfinite residual'
      residual=maxval(abs(f))
      root_error=maxval(abs(x-1._wp))
      if (residual>1.e-8_wp.or.root_error>1.e-8_wp) error stop 'root or residual mismatch'
      print '(a,2f8.3,a,2f14.10)', 'Start:',starts(:,case_number),' root:',x
      print '(a,i0,1x,a)', 'status=',status,message
      print '(a,i0,a,i0,a,es10.2,a,es10.2)', 'function calls=',calls,' Jacobian calls=',jac_calls, &
         ' residual=',residual,' root error=',root_error
   end do
   print '(a)', 'PASS nlesolver-rosenbrock-system'
end program
