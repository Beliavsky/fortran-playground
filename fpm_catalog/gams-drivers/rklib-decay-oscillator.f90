! Adapted from the author integration API example; shared analytic IVP and checks.
! BSD 3-Clause License
! 
! Copyright (c) 2022-2023, Jacob Williams
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
module ode_problem
   use rklib_module, only: rk_class, wp=>rk_module_rk
   implicit none
   integer :: rhs_calls=0
contains
   subroutine equations(me,t,y,dy)
      class(rk_class), intent(inout) :: me
      real(wp), intent(in) :: t,y(:)
      real(wp), intent(out) :: dy(:)
      rhs_calls=rhs_calls+1
      dy=[-y(1),y(3),-y(2)]
   end subroutine
   function exact(t) result(y)
      real(wp), intent(in) :: t
      real(wp) :: y(3)
      y=[exp(-t),cos(t),-sin(t)]
   end function
end module
program checked_nonstiff_ivp
   use ode_problem
   use ieee_arithmetic, only: ieee_is_finite
   use rklib_module, only: rk4_class
   implicit none
   type(rk4_class) :: solver
   real(wp) :: t,target,y(3),period,solution_error,energy_error,max_error,max_energy_error
   integer :: checkpoint,status
   real(wp) :: next_y(3),step,refinement_errors(2),ratio
   integer :: refinement,steps
   period=2._wp*acos(-1._wp)
   t=0._wp; y=exact(t); rhs_calls=0
   max_error=0._wp; max_energy_error=0._wp
   call solver%initialize(n=3,f=equations)
   step=0.01_wp
   print '(a)', '       t      max state error      oscillator energy error'
   do checkpoint=1,10
      target=period*real(checkpoint,wp)/10._wp
      call solver%integrate(t,y,step,target,next_y)
      call solver%status(istatus=status)
      if (status/=0) error stop 'RK4 solver status'
      y=next_y
      t=target
      if (.not.ieee_is_finite(t).or..not.all(ieee_is_finite(y))) error stop 'nonfinite ODE result'
      if (abs(t-target)>1.e-12_wp) error stop 'incorrect output time'
      solution_error=maxval(abs(y-exact(target)))
      energy_error=abs(y(2)**2+y(3)**2-1._wp)
      if (solution_error>1.e-8_wp.or.energy_error>2.e-8_wp) error stop 'independent ODE accuracy'
      if (y(1)<0._wp) error stop 'negative decay state'
      max_error=max(max_error,solution_error)
      max_energy_error=max(max_energy_error,energy_error)
      print '(f10.6,2es22.10)', t,solution_error,energy_error
   end do
   if (rhs_calls<=0) error stop 'no RHS evaluations'
   print '(a,es12.4)', 'Maximum checkpoint state error: ', max_error
   print '(a,es12.4)', 'Maximum checkpoint energy error: ', max_energy_error
   print '(a,i0)', 'RHS callback calls (checkpoint run): ', rhs_calls
   print '(a,i0)', 'Final solver status: ', status
   ! Separate endpoint convergence experiment; not part of the checkpoint counters.
   do refinement=1,2
      steps=100*2**(refinement-1)
      rhs_calls=0
      call solver%initialize(n=3,f=equations)
      call solver%integrate(0._wp,exact(0._wp),period/real(steps,wp),period,y)
      call solver%status(istatus=status)
      if (status/=0.or..not.all(ieee_is_finite(y))) error stop 'RK4 refinement run'
      refinement_errors(refinement)=maxval(abs(y-exact(period)))
      if (refinement_errors(refinement)<=0._wp) error stop 'invalid convergence error'
      print '(a,i0,a,es12.4,a,i0)', 'RK4 nominal steps: ',steps, &
         '; endpoint state error: ',refinement_errors(refinement),'; RHS calls: ',rhs_calls
   end do
   ratio=refinement_errors(1)/refinement_errors(2)
   if (ratio<12._wp.or.ratio>20._wp) error stop 'RK4 fourth-order step refinement'
   print '(a,f12.6)', 'Coarse/fine error ratio (fourth order suggests 16): ', ratio
   print '(a)', 'PASS rklib-decay-oscillator'
end program
