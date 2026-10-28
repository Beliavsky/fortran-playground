! Copyright (c) 2022 minpack contributors
! 
! Permission is hereby granted, free of charge, to any person obtaining a copy
! of this software and associated documentation files (the "Software"), to deal
! in the Software without restriction, including without limitation the rights
! to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
! copies of the Software, and to permit persons to whom the Software is
! furnished to do so, subject to the following conditions:
! 
! The above copyright notice and this permission notice shall be included in
! all copies or substantial portions of the Software.
! 
! THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
! IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
! FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
! AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
! LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
! OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
! THE SOFTWARE.
! 
! -----------------------------------------------------------------------------
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
!
! Adapted from jacobwilliams/minpack examples/example_lmdif1.f90 at
! c0b5aea9fcd2b83865af921a7a7e881904f8d3c2.
! Changes: module callback, shared Bard-15 model, independent reference checks.
module bard_problem
   use minpack_module, only: wp
   implicit none
   real(wp), parameter :: observations(15) = [ &
      .14_wp,.18_wp,.22_wp,.25_wp,.29_wp,.32_wp,.35_wp,.39_wp, &
      .37_wp,.58_wp,.73_wp,.96_wp,1.34_wp,2.10_wp,4.39_wp]
   real(wp), parameter :: expected(3) = [.08241058_wp,1.133037_wp,2.343695_wp]
   real(wp), parameter :: expected_norm = .09063596_wp
   integer :: calls = 0
contains
   subroutine evaluate(x,residual)
      real(wp), intent(in) :: x(3)
      real(wp), intent(out) :: residual(15)
      integer :: i
      do i=1,15
         residual(i) = observations(i) - (x(1)+real(i,wp)/ &
            (x(2)*real(16-i,wp)+x(3)*real(min(i,16-i),wp)))
      end do
   end subroutine

   subroutine callback(m,n,x,residual,iflag)
      integer, intent(in) :: m,n
      real(wp), intent(in) :: x(n)
      real(wp), intent(out) :: residual(m)
      integer, intent(inout) :: iflag
      if (iflag>0) then
         calls = calls + 1
         call evaluate(x,residual)
      end if
   end subroutine
end module

program gams_minpack_bard
   use minpack_module, only: lmdif1
   use bard_problem
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer, parameter :: n=3,m=15,lwa=m*n+5*n+m
   real(wp) :: x(n),residual(m),work(lwa),residual_norm,parameter_error
   integer :: info,ipvt(n)
   x = [1.0_wp,1.0_wp,1.0_wp]
   call lmdif1(callback,m,n,x,residual,1.0e-10_wp,info,ipvt,work,lwa)
   call evaluate(x,residual)
   residual_norm = norm2(residual)
   parameter_error = maxval(abs(x-expected))
   if (.not. all(ieee_is_finite(x)) .or. .not. ieee_is_finite(residual_norm)) error stop 'Nonfinite fit'
   if (info<1 .or. info>4) error stop 'MINPACK did not converge'
   if (parameter_error>2.0e-4_wp) error stop 'Reference parameters differ'
   if (abs(residual_norm-expected_norm)>1.0e-7_wp) error stop 'Reference residual norm differs'
   print '(a)', 'GAMS G1b: Bard-15 nonlinear least squares, MINPACK lmdif1.'
   print '(a,3f14.8)', 'Parameters: ',x
   print '(a,es12.3)', 'Maximum parameter error: ',parameter_error
   print '(a,es16.8)', 'Independent residual norm: ',residual_norm
   print '(a,i0)', 'Residual callback calls: ',calls
   print '(a,i0)', 'Solver termination code: ',info
   print '(a)', 'PASS minpack-bard'
end program
