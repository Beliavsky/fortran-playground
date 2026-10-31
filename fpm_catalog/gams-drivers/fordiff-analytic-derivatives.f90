! Adapted author API patterns; shared analytic derivative checks.
! BSD 3-Clause License
! 
! Copyright (c) 2023, Seyed Ali Ghasemi
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
module checked_functions
   use fordiff, only: rk,derivative
   implicit none
contains
   function smooth(x) result(y)
      real(rk), intent(in) :: x
      real(rk) :: y
      y=exp(x)*sin(x)
   end function
   function smooth_complex(x) result(y)
      complex(rk), intent(in) :: x
      complex(rk) :: y
      ! Complex step requires an analytic complex extension.
      y=exp(x)*sin(x)
   end function
end module
program checked_differentiation
   use checked_functions
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
   real(rk), parameter :: points(4)=[-0.5_rk,0._rk,0.5_rk,1._rk]
   character(8), parameter :: methods(4)=[character(8)::'forward','backward','central','complex']
   real(rk), parameter :: tolerance(4)=[5.e-5_rk,5.e-5_rk,1.e-9_rk,5.e-14_rk]
   real(rk) :: x,answer,reference,scaled_error,max_error(4)
   integer :: i,method
   max_error=0._rk
   do i=1,size(points)
      x=points(i)
      reference=exp(x)*(sin(x)+cos(x))
      do method=1,4
         if (method==4) then
            answer=derivative(f=smooth_complex,x=x,h=1.e-20_rk)
         else
            answer=derivative(f=smooth,x=x,h=1.e-5_rk,method=trim(methods(method)))
         end if
         if (.not.ieee_is_finite(answer)) error stop 'nonfinite derivative'
         scaled_error=abs(answer-reference)/max(1._rk,abs(reference))
         if (scaled_error>tolerance(method)) error stop 'analytic derivative mismatch'
         max_error(method)=max(max_error(method),scaled_error)
         print '(a,f5.1,1x,a8,a,es13.5)', 'x=',x,methods(method),' derivative=',answer
      end do
   end do
   do method=1,4
      print '(a8,a,es12.4)',methods(method),' maximum scaled analytic error: ',max_error(method)
   end do
   print '(a)', 'PASS fordiff-analytic-derivatives'
end program
