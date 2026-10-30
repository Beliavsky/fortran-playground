! Adapted author interpolation API patterns; shared deterministic data and checks.
! finterp: Modern Fortran Multidimensional Linear Interpolation
! https://github.com/jacobwilliams/finterp
! 
! Copyright (c) 2016-2022, Jacob Williams
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
program checked_interpolation
   use iso_fortran_env, only: wp=>real64
   use ieee_arithmetic, only: ieee_is_finite
   use linear_interpolation_module, only: linear_interp_1d
   implicit none
   integer, parameter :: n=6
   real(wp), parameter :: x(n)=[0._wp,0.25_wp,0.5_wp,1._wp,2._wp,3._wp]
   real(wp) :: f(n),query,answer,previous,reference,theta
   real(wp) :: node_error,affine_error,linear_difference,bound_violation,decrease
   integer :: problem,i,j,evaluations
   type(linear_interp_1d) :: interpolator
   integer :: status
   do problem=1,2
      if (problem==1) then
         f=2._wp*x-1._wp
         print '(a)', 'Case: affine data f(x)=2*x-1'
      else
         f=[0._wp,0.01_wp,0.02_wp,0.9_wp,0.95_wp,1._wp]
         print '(a)', 'Case: steep monotone data'
      end if
      call interpolator%initialize(x,f,status)
      if (status/=0) error stop 'interpolator initialization'
      evaluations=0; node_error=0._wp; affine_error=0._wp; linear_difference=0._wp
      bound_violation=0._wp; decrease=0._wp
      do i=1,n
         call evaluate(x(i),answer)
         node_error=max(node_error,abs(answer-f(i)))
      end do
      if (node_error>1.e-12_wp) error stop 'interpolation at original nodes'
      previous=f(1)
      print '(a)', '  Interval midpoint       Interpolated value'
      do i=1,n-1
         do j=0,20
            theta=real(j,wp)/20._wp
            query=x(i)+theta*(x(i+1)-x(i))
            call evaluate(query,answer)
            reference=(1._wp-theta)*f(i)+theta*f(i+1)
            linear_difference=max(linear_difference,abs(answer-reference))
            bound_violation=max(bound_violation,f(i)-answer,answer-f(i+1))
            decrease=max(decrease,previous-answer)
            if (problem==1) affine_error=max(affine_error,abs(answer-(2._wp*query-1._wp)))
            if (j==10) print '(2f24.14)', query,answer
            previous=answer
         end do
      end do
      if (bound_violation>1.e-12_wp.or.decrease>1.e-12_wp) error stop 'sampled monotonicity or overshoot'
      if (affine_error>1.e-12_wp) error stop 'affine preservation'
      if (linear_difference>1.e-12_wp) error stop 'piecewise linear reference'
      print '(a,es12.4)', 'Maximum node error: ',node_error
      if (problem==1) print '(a,es12.4)', 'Maximum affine reproduction error: ',affine_error
      print '(a,es12.4)', 'Maximum difference from piecewise linear: ',linear_difference
      print '(a,es12.4)', 'Maximum sampled local bound violation: ',bound_violation
      print '(a,es12.4)', 'Maximum sampled decrease: ',decrease
      print '(a,i0)', 'Evaluator calls: ',evaluations
   end do
   print '(a)', 'PASS finterp-shape-interpolation'
contains
   subroutine evaluate(t,value)
      real(wp), intent(in) :: t
      real(wp), intent(out) :: value
      evaluations=evaluations+1
      call interpolator%evaluate(t,value,status)
      if (status/=0.or..not.ieee_is_finite(value)) error stop 'interpolation evaluation'
   end subroutine
end program
