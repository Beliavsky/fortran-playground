! Adapted from QUADPACK test_qags, with an additional logarithmic singularity.
! BSD 3-Clause License
! 
! Copyright (c) 2021-2022, Jacob Williams
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
! 
! ------------------------------------------------------------------
! 
! The original QUADPACK was from the SLATEC Library, which is a public domain
! work of the United States government.

module singular_integrands
   use iso_fortran_env, only: wp=>real64
   implicit none
   integer :: integrand_case=1, calls=0
contains
   function integrand(x) result(y)
      real(wp), intent(in) :: x
      real(wp) :: y
      if (x<=0._wp) error stop 'integrable singularity evaluated at endpoint'
      calls=calls+1
      y=1._wp/sqrt(x)
      if (integrand_case==2) y=y*log(x)
   end function
end module
program endpoint_singularities
   use quadpack, only: dqags
   use singular_integrands
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer, parameter :: limit=300
   integer :: neval, status, last, iwork(limit)
   real(wp) :: answer, estimate, actual_error, work(4*limit)
   real(wp), parameter :: expected(2)=[2._wp,-4._wp]
   do integrand_case=1,2
      calls=0
      call dqags(integrand,0._wp,1._wp,1.e-10_wp,1.e-10_wp, &
         answer,estimate,neval,status,limit,4*limit,last,iwork,work)
      if (status/=0.or.neval/=calls) error stop 'QUADPACK status/evaluation count'
      if (.not.ieee_is_finite(answer).or..not.ieee_is_finite(estimate)) error stop 'nonfinite result'
      if (estimate<0._wp) error stop 'negative error estimate'
      actual_error=abs(answer-expected(integrand_case))
      if (actual_error>1.e-8_wp) error stop 'independent singular-integral accuracy'
      if (integrand_case==1) then
         print '(a)', 'Case: 1/sqrt(x) on [0,1]; exact integral 2'
      else
         print '(a)', 'Case: log(x)/sqrt(x) on [0,1]; exact integral -4'
      end if
      print '(a,es22.14)', 'Computed integral: ', answer
      print '(a,es12.4)', 'Actual absolute error: ', actual_error
      print '(a,es12.4)', 'Reported error estimate: ', estimate
      print '(a,i0)', 'Integrand callback calls: ', calls
      print '(a,i0)', 'Solver status: ', status
   end do
   print '(a)', 'PASS quadpack-endpoint-singular'
end program
