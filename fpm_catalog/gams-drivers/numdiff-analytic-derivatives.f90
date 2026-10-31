! Adapted author API patterns; shared analytic derivative checks.
! NumDiff -- Numerical Differentiation Library
! https://github.com/jacobwilliams/NumDiff
! 
! Copyright (c) 2016-2026, Jacob Williams
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
! 
! Minpack Copyright Notice (1999) University of Chicago.  All rights reserved
! 
! Redistribution and use in source and binary forms, with or
! without modification, are permitted provided that the
! following conditions are met:
! 
! 1. Redistributions of source code must retain the above
! copyright notice, this list of conditions and the following
! disclaimer.
! 
! 2. Redistributions in binary form must reproduce the above
! copyright notice, this list of conditions and the following
! disclaimer in the documentation and/or other materials
! provided with the distribution.
! 
! 3. The end-user documentation included with the
! redistribution, if any, must include the following
! acknowledgment:
! 
!    "This product includes software developed by the
!    University of Chicago, as Operator of Argonne National
!    Laboratory.
! 
! Alternately, this acknowledgment may appear in the software
! itself, if and wherever such third-party acknowledgments
! normally appear.
! 
! 4. WARRANTY DISCLAIMER. THE SOFTWARE IS SUPPLIED "AS IS"
! WITHOUT WARRANTY OF ANY KIND. THE COPYRIGHT HOLDER, THE
! UNITED STATES, THE UNITED STATES DEPARTMENT OF ENERGY, AND
! THEIR EMPLOYEES: (1) DISCLAIM ANY WARRANTIES, EXPRESS OR
! IMPLIED, INCLUDING BUT NOT LIMITED TO ANY IMPLIED WARRANTIES
! OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, TITLE
! OR NON-INFRINGEMENT, (2) DO NOT ASSUME ANY LEGAL LIABILITY
! OR RESPONSIBILITY FOR THE ACCURACY, COMPLETENESS, OR
! USEFULNESS OF THE SOFTWARE, (3) DO NOT REPRESENT THAT USE OF
! THE SOFTWARE WOULD NOT INFRINGE PRIVATELY OWNED RIGHTS, (4)
! DO NOT WARRANT THAT THE SOFTWARE WILL FUNCTION
! UNINTERRUPTED, THAT IT IS ERROR-FREE OR THAT ANY ERRORS WILL
! BE CORRECTED.
! 
! 5. LIMITATION OF LIABILITY. IN NO EVENT WILL THE COPYRIGHT
! HOLDER, THE UNITED STATES, THE UNITED STATES DEPARTMENT OF
! ENERGY, OR THEIR EMPLOYEES: BE LIABLE FOR ANY INDIRECT,
! INCIDENTAL, CONSEQUENTIAL, SPECIAL OR PUNITIVE DAMAGES OF
! ANY KIND OR NATURE, INCLUDING BUT NOT LIMITED TO LOSS OF
! PROFITS OR LOSS OF DATA, FOR ANY REASON WHATSOEVER, WHETHER
! SUCH LIABILITY IS ASSERTED ON THE BASIS OF CONTRACT, TORT
! (INCLUDING NEGLIGENCE OR STRICT LIABILITY), OR OTHERWISE,
! EVEN IF ANY OF SAID PARTIES HAS BEEN WARNED OF THE
! POSSIBILITY OF SUCH LOSS OR DAMAGES.
module checked_functions
   use numdiff_kinds_module, only: wp
   use diff_module, only: diff_func
   implicit none
contains
   function smooth(me,x) result(y)
      class(diff_func), intent(inout) :: me
      real(wp), intent(in) :: x
      real(wp) :: y
      y=exp(x)*sin(x)
   end function
end module
program checked_differentiation
   use checked_functions
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
   real(wp), parameter :: points(4)=[-0.5_wp,0._wp,0.5_wp,1._wp]
   real(wp), parameter :: tolerance(3)=[1.e-8_wp,1.e-8_wp,1.e-6_wp]
   type(diff_func) :: d
   real(wp) :: x,answer,estimate,reference(3),scaled_error,max_error
   integer :: i,order,status
   call d%set_function(smooth)
   max_error=0._wp
   do i=1,size(points)
      x=points(i)
      reference=[exp(x)*(sin(x)+cos(x)),2._wp*exp(x)*cos(x),2._wp*exp(x)*(cos(x)-sin(x))]
      do order=1,3
         ! Endpoints x=-0.5 and x=1 exercise one-sided formulas.
         call d%compute_derivative(order,x,-0.5_wp,1._wp,tolerance(order),0._wp,answer,estimate,status)
         print '(a,i1,a,i0,a,es10.2)', 'order=',order,' status=',status,' estimated error=',estimate
         if (status/=0) error stop 'requested differentiation tolerance not met'
         if (.not.ieee_is_finite(answer).or..not.ieee_is_finite(estimate)) error stop 'nonfinite derivative'
         if (estimate<0._wp.or.estimate>tolerance(order)) error stop 'unexpected error estimate'
         scaled_error=abs(answer-reference(order))/max(1._wp,abs(reference(order)))
         if (scaled_error>max(1.e-7_wp,tolerance(order))) error stop 'analytic derivative mismatch'
         if (abs(answer-reference(order))>estimate+64*epsilon(x)*max(1._wp,abs(reference(order)))) &
            error stop 'analytic error exceeds estimated bound plus rounding allowance'
         max_error=max(max_error,scaled_error)
         print '(a,f5.1,a,i1,a,es13.5,a,es10.2)', 'x=',x,' order=',order,' derivative=',answer,' estimate=',estimate
      end do
   end do
   print '(a,es12.4)', 'Maximum scaled analytic error: ',max_error
   print '(a)', 'PASS numdiff-analytic-derivatives'
end program
