! Adapted from the author integration API example; shared analytic IVP and checks.
! Modern Fortran Edition of the DOP853 ODE Solver
! https://github.com/jacobwilliams/dop853
! 
! Copyright (c) 2015-2022, Jacob Williams
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
!   Original DOP853 License
! --------------------------------------------------------------------------------
! 
! Copyright (c) 2004, Ernst Hairer
! 
! Redistribution and use in source and binary forms, with or without
! modification, are permitted provided that the following conditions are
! met:
! 
! - Redistributions of source code must retain the above copyright
! notice, this list of conditions and the following disclaimer.
! 
! - Redistributions in binary form must reproduce the above copyright
! notice, this list of conditions and the following disclaimer in the
! documentation and/or other materials provided with the distribution.
! 
! THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS �AS
! IS� AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
! TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
! PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE REGENTS OR
! CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
! EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
! PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
! PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
! LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
! NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
! SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
module ode_problem
   use dop853_module, only: dop853_class, wp=>dop853_wp
   implicit none
   integer :: rhs_calls=0
contains
   subroutine equations(me,t,y,dy)
      class(dop853_class), intent(inout) :: me
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
   implicit none
   type(dop853_class) :: solver
   real(wp) :: t,target,y(3),period,solution_error,energy_error,max_error,max_energy_error
   integer :: checkpoint,status
   logical :: initialized
   period=2._wp*acos(-1._wp)
   t=0._wp; y=exact(t); rhs_calls=0
   max_error=0._wp; max_energy_error=0._wp
   call solver%initialize(n=3,fcn=equations,status_ok=initialized)
   if (.not.initialized) error stop 'DOP853 initialization'
   print '(a)', '       t      max state error      oscillator energy error'
   do checkpoint=1,10
      target=period*real(checkpoint,wp)/10._wp
      call solver%integrate(t,y,target,[1.e-10_wp],[1.e-10_wp],0,status)
      if (status/=1) error stop 'DOP853 did not complete integration'
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
   print '(a)', 'PASS dop853-decay-oscillator'
end program
