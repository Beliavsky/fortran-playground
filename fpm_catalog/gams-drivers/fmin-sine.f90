! BSD 3-Clause License
! 
! Copyright (c) 2021, Jacob Williams
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
! Adapted from jacobwilliams/fmin test/test.f90 at
! 3d094fba0e9b98d132414f8442c7c76d32da1d30.
! Changes: module callback, finite/accuracy checks and explicit output.
module sine_objective
   use fmin_module, only: wp => fmin_rk
   implicit none
   integer :: calls = 0
contains
   function objective(x) result(f)
      real(wp), intent(in) :: x
      real(wp) :: f
      calls = calls + 1
      f = sin(x)
   end function
end module

program gams_fmin_sine
   use fmin_module, only: fmin
   use sine_objective
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   real(wp) :: x, expected, value
   expected = -acos(-1.0_wp)/2
   x = fmin(objective, -4.0_wp, 0.0_wp, 1.0e-8_wp)
   value = sin(x)
   if (.not. ieee_is_finite(x)) error stop 'Nonfinite minimizer'
   if (abs(x-expected)>1.0e-6_wp .or. abs(value+1)>1.0e-12_wp) error stop 'Incorrect minimum'
   print '(a)', 'GAMS G1a: minimize sin(x) on the search interval [-4,0].'
   print '(a,f16.10)', 'Computed x: ', x
   print '(a,es12.3)', 'Absolute solution error: ', abs(x-expected)
   print '(a,f16.10)', 'Independently evaluated objective: ', value
   print '(a,i0)', 'Objective calls: ', calls
   print '(a)', 'PASS fmin-sine'
end program
