! Adapted from quadrature-fortran author tests; see the retained BSD license below.
! quadrature-fortran: Adaptive Gaussian Quadrature with Modern Fortran
! https://github.com/jacobwilliams/quadrature-fortran
! 
! Copyright (c) 2019-2021, Jacob Williams
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
! !-----------------------------------------------------------------------------------------
! !
! !  quadrature-fortran includes code from SLATEC, a public domain library.
! !
! !-----------------------------------------------------------------------------------------

module smooth_integrands
   use iso_fortran_env, only: wp=>real64
   use quadrature_module, only: integration_class_1d
   implicit none
   integer :: integrand_case=1, calls=0
contains
   function integrand(me,x) result(y)
      class(integration_class_1d), intent(inout) :: me
      real(wp), intent(in) :: x
      real(wp) :: y
      calls=calls+1
      if (integrand_case==1) then
         y=exp(x)
      else
         y=cos(20._wp*x)
      end if
   end function
end module
program smooth_finite_integrals
   use smooth_integrands
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
   type(integration_class_1d) :: integral
   integer :: status
   real(wp) :: answer, estimate, expected, actual_error
   do integrand_case=1,2
      calls=0
      call integral%initialize(fx=integrand,xl=0._wp,xu=1._wp,tolx=1.e-10_wp,methodx=8)
      call integral%integrate(answer,status,estimate)
      ! quadrature-fortran uses 1 for successful termination, unlike QUADPACK.
      if (status/=1) error stop 'quadrature-fortran status'
      if (.not.ieee_is_finite(answer).or..not.ieee_is_finite(estimate)) error stop 'nonfinite result'
      if (integrand_case==1) then
         expected=exp(1._wp)-1._wp
         print '(a)', 'Case: exp(x) on [0,1]'
      else
         expected=sin(20._wp)/20._wp
         print '(a)', 'Case: cos(20*x) on [0,1]'
      end if
      actual_error=abs(answer-expected)
      if (actual_error>1.e-9_wp) error stop 'independent quadrature accuracy'
      print '(a,es22.14)', 'Computed integral: ', answer
      print '(a,es12.4)', 'Actual absolute error: ', actual_error
      print '(a,es12.4)', 'Reported error estimate: ', estimate
      print '(a,i0)', 'Integrand callback calls: ', calls
      print '(a,i0)', 'Solver status: ', status
   end do
   print '(a)', 'PASS quadrature-fortran-smooth'
end program
