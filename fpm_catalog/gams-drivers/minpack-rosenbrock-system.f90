! Adapted author solver API patterns; common nonlinear system and checked root.
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
module system_equations
   use minpack_module, only: wp,hybrd1
   implicit none
   integer :: calls=0
contains
   subroutine equations(n,x,f,iflag)
      integer, intent(in) :: n
      integer, intent(inout) :: iflag
      real(wp), intent(in) :: x(n)
      real(wp), intent(out) :: f(n)
      calls=calls+1
      f=[1._wp-x(1),10._wp*(x(2)-x(1)**2)]
   end subroutine
end module
program checked_nonlinear_system
   use system_equations
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer, parameter :: n=2,lwa=n*(3*n+13)/2
   real(wp), parameter :: starts(2,2)=reshape([-1.2_wp,1._wp,2._wp,2._wp],[2,2])
   real(wp) :: x(n),f(n),reference_f(n),wa(lwa),root_error,residual
   integer :: case_number,info
   do case_number=1,2
      x=starts(:,case_number)
      calls=0
      call hybrd1(equations,n,x,f,1.e-10_wp,info,wa,lwa)
      if (info/=1) error stop 'MINPACK did not report convergence'
      if (.not.all(ieee_is_finite(x)).or..not.all(ieee_is_finite(f))) error stop 'nonfinite solver result'
      reference_f=[1._wp-x(1),10._wp*(x(2)-x(1)**2)]
      residual=maxval(abs(reference_f))
      root_error=maxval(abs(x-1._wp))
      if (residual>1.e-8_wp.or.root_error>1.e-8_wp) error stop 'root or residual mismatch'
      if (maxval(abs(f-reference_f))>1.e-12_wp) error stop 'returned residual mismatch'
      print '(a,2f8.3,a,2f14.10)', 'Start:',starts(:,case_number),' root:',x
      print '(a,i0,a,i0,a,es10.2,a,es10.2)', 'info=',info,' function calls=',calls, &
         ' residual=',residual,' root error=',root_error
   end do
   print '(a)', 'PASS minpack-rosenbrock-system'
end program
