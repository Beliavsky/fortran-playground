! Adapted author interpolation API patterns; shared deterministic data and checks.
! BSPLINE-FORTRAN: Multidimensional B-Spline Interpolation of Data on a Regular Grid
! 
! Copyright (c) 2015-2023, Jacob Williams
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
! !  BSPLINE-FORTRAN includes code from CMLIB, a public domain library
! !  from the National Institute of Standards and Technology (NIST)
! !
! !  The CMLIB license is given below:
! !
! !-----------------------------------------------------------------------------------------
! 
! The research software provided on this web site ("software") is provided by NIST as a
! public service. You may use, copy and distribute copies of the software in any medium,
! provided that you keep intact this entire notice. You may improve, modify and create
! derivative works of the software or any portion of the software, and you may copy and
! distribute such modifications or works. Modified works should carry a notice stating that
! you changed the software and should note the date and nature of any such change. Please
! explicitly acknowledge the National Institute of Standards and Technology as the source
! of the software.
! 
! The software is expressly provided "AS IS." NIST MAKES NO WARRANTY OF ANY KIND, EXPRESS,
! IMPLIED, IN FACT OR ARISING BY OPERATION OF LAW, INCLUDING, WITHOUT LIMITATION, THE
! IMPLIED WARRANTY OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, NON-INFRINGEMENT
! AND DATA ACCURACY. NIST NEITHER REPRESENTS NOR WARRANTS THAT THE OPERATION OF THE SOFTWARE
! WILL BE UNINTERRUPTED OR ERROR-FREE, OR THAT ANY DEFECTS WILL BE CORRECTED. NIST DOES NOT
! WARRANT OR MAKE ANY REPRESENTATIONS REGARDING THE USE OF THE SOFTWARE OR THE RESULTS
! THEREOF, INCLUDING BUT NOT LIMITED TO THE CORRECTNESS, ACCURACY, RELIABILITY, OR
! USEFULNESS OF THE SOFTWARE.
! 
! You are solely responsible for determining the appropriateness of using and distributing
! the software and you assume all risks associated with its use, including but not limited
! to the risks and costs of program errors, compliance with applicable laws, damage to or
! loss of data, programs or equipment, and the unavailability or interruption of operation.
! This software is not intended to be used in any situation where a failure could cause risk
! of injury or damage to property.  The software was developed by NIST employees. NIST
! employee contributions are not subject to copyright protection within the United States.
! 
! !-----------------------------------------------------------------------------------------
! ! LAPACK License
! !-----------------------------------------------------------------------------------------
! 
! Copyright (c) 1992-2022 The University of Tennessee and The University
!                         of Tennessee Research Foundation.  All rights
!                         reserved.
! Copyright (c) 2000-2022 The University of California Berkeley. All
!                         rights reserved.
! Copyright (c) 2006-2022 The University of Colorado Denver.  All rights
!                         reserved.
! 
! $COPYRIGHT$
! 
! Additional copyrights may follow
! 
! $HEADER$
! 
! Redistribution and use in source and binary forms, with or without
! modification, are permitted provided that the following conditions are
! met:
! 
! - Redistributions of source code must retain the above copyright
!   notice, this list of conditions and the following disclaimer.
! 
! - Redistributions in binary form must reproduce the above copyright
!   notice, this list of conditions and the following disclaimer listed
!   in this license in the documentation and/or other materials
!   provided with the distribution.
! 
! - Neither the name of the copyright holders nor the names of its
!   contributors may be used to endorse or promote products derived from
!   this software without specific prior written permission.
! 
! The copyright holders provide no reassurances that the source code
! provided does not infringe any patent, copyright, or any other
! intellectual property rights of third parties.  The copyright holders
! disclaim any liability to any recipient for claims brought against
! recipient by any third party for infringement of that parties
! intellectual property rights.
! 
! THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
! "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
! LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
! A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
! OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
! SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
! LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
! DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
! THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
! (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
! OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
! 
! !-----------------------------------------------------------------------------------------
! !
! !  BSPLINE-FORTRAN includes code from the SLATEC Common Mathematical Library,
! !  A public domain work of the U.S. government.
! !
! !  https://netlib.org/slatec/
! !
! !-----------------------------------------------------------------------------------------
program checked_interpolation
   use iso_fortran_env, only: wp=>real64
   use ieee_arithmetic, only: ieee_is_finite
   use bspline_module, only: bspline_1d
   use bspline_kinds_module, only: ip
   implicit none
   integer, parameter :: n=6
   real(wp), parameter :: x(n)=[0._wp,0.25_wp,0.5_wp,1._wp,2._wp,3._wp]
   real(wp) :: f(n),query,answer,previous,reference,theta
   real(wp) :: node_error,affine_error,linear_difference,bound_violation,decrease
   integer :: problem,i,j,evaluations
   type(bspline_1d) :: interpolator
   integer(ip) :: status
   real(wp) :: cubic_error,derivative_error
   do problem=1,2
      if (problem==1) then
         f=2._wp*x-1._wp
         print '(a)', 'Case: affine data f(x)=2*x-1'
      else
         f=[0._wp,0.01_wp,0.02_wp,0.9_wp,0.95_wp,1._wp]
         print '(a)', 'Case: steep monotone data'
      end if
      call interpolator%initialize(x,f,2_ip,status)
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
   ! Order 4 means cubic pieces. This separate check does not assert shape preservation.
   f=polynomial(x)
   call interpolator%initialize(x,f,4_ip,status)
   if (status/=0) error stop 'cubic B-spline initialization'
   cubic_error=0._wp; derivative_error=0._wp
   do j=0,100
      query=x(1)+(x(n)-x(1))*real(j,wp)/100._wp
      call interpolator%evaluate(query,0_ip,answer,status)
      if (status/=0.or..not.ieee_is_finite(answer)) error stop 'cubic value evaluation'
      cubic_error=max(cubic_error,abs(answer-polynomial(query)))
      call interpolator%evaluate(query,1_ip,answer,status)
      if (status/=0.or..not.ieee_is_finite(answer)) error stop 'cubic derivative evaluation'
      derivative_error=max(derivative_error,abs(answer-(-2._wp+query+3._wp*query**2)))
   end do
   if (cubic_error>1.e-10_wp.or.derivative_error>1.e-10_wp) error stop 'cubic reproduction'
   print '(a,es12.4)', 'Cubic reproduction maximum error: ',cubic_error
   print '(a,es12.4)', 'Cubic first derivative maximum error: ',derivative_error
   call interpolator%destroy()
   print '(a)', 'PASS bspline-fortran-shape-interpolation'
contains
   subroutine evaluate(t,value)
      real(wp), intent(in) :: t
      real(wp), intent(out) :: value
      evaluations=evaluations+1
      call interpolator%evaluate(t,0_ip,value,status)
      if (status/=0.or..not.ieee_is_finite(value)) error stop 'interpolation evaluation'
   end subroutine
   elemental function polynomial(t) result(value)
      real(wp), intent(in) :: t
      real(wp) :: value
      value=1._wp-2._wp*t+0.5_wp*t**2+t**3
   end function
end program
