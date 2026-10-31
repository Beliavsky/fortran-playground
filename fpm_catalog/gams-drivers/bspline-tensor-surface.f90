! Author API patterns adapted on 2026-10-30: checked nonuniform 2D surfaces.
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
program checked_surface_interpolation
   use iso_fortran_env, only: wp=>real64
   use bspline_module, only: bspline_2d
   use bspline_kinds_module, only: ip
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer, parameter :: nx=6,ny=5
   real(wp), parameter :: x(nx)=[-1._wp,-0.6_wp,0._wp,0.3_wp,1._wp,2._wp]
   real(wp), parameter :: y(ny)=[-2._wp,-0.75_wp,0._wp,0.5_wp,1.5_wp]
   real(wp) :: f(nx,ny),u,v,s,t,answer,reference,node_error,formula_error,bounds_error,reproduction_error
   integer :: problem,i,j,ix,iy,calls
   type(bspline_2d) :: interpolator
   integer(ip) :: status
   real(wp) :: polynomial_errors(4),computed(4),expected(4)
   do problem=1,2
      do j=1,ny
         do i=1,nx
            if (problem==1) then
               f(i,j)=surface(x(i),y(j))
            else
               f(i,j)=x(i)**2+2._wp*y(j)**2+x(i)*y(j)
            end if
         end do
      end do
      call interpolator%initialize(x,y,f,2_ip,2_ip,status)
      if (status/=0) error stop 'bilinear B-spline initialization'
      calls=0;node_error=0._wp;formula_error=0._wp;bounds_error=0._wp;reproduction_error=0._wp
      do j=1,ny
         do i=1,nx
            call evaluate(x(i),y(j),answer)
            node_error=max(node_error,abs(answer-f(i,j)))
         end do
      end do
      do j=1,ny-1
         do i=1,nx-1
            do iy=0,4
               t=real(iy,wp)/4._wp
               v=y(j)+t*(y(j+1)-y(j))
               do ix=0,4
                  s=real(ix,wp)/4._wp
                  u=x(i)+s*(x(i+1)-x(i))
                  call evaluate(u,v,answer)
                  reference=(1._wp-s)*(1._wp-t)*f(i,j)+s*(1._wp-t)*f(i+1,j) &
                     +(1._wp-s)*t*f(i,j+1)+s*t*f(i+1,j+1)
                  formula_error=max(formula_error,abs(answer-reference))
                  bounds_error=max(bounds_error,minval(f(i:i+1,j:j+1))-answer,answer-maxval(f(i:i+1,j:j+1)))
                  if (problem==1) reproduction_error=max(reproduction_error,abs(answer-surface(u,v)))
               end do
            end do
         end do
      end do
      if (max(node_error,formula_error,bounds_error,reproduction_error)>1.e-11_wp) &
         error stop 'bilinear interpolation mismatch'
      print '(a,i0,a,i0)', 'Surface case ',problem,' evaluations=',calls
      print '(a,3es13.4)', 'Node / bilinear formula / corner bound errors:',node_error,formula_error,bounds_error
      if (problem==1) print '(a,es13.4)', 'Analytic bilinear surface error:',reproduction_error
   end do
   do j=1,ny
      do i=1,nx
         f(i,j)=polynomial(x(i),y(j))
      end do
   end do
   ! Order 4 means cubic pieces in each coordinate, not degree 4.
   call interpolator%initialize(x,y,f,4_ip,4_ip,status)
   if (status/=0) error stop 'bicubic B-spline initialization'
   polynomial_errors=0._wp;calls=0
   do iy=0,10
      v=y(1)+(y(ny)-y(1))*real(iy,wp)/10._wp
      do ix=0,10
         u=x(1)+(x(nx)-x(1))*real(ix,wp)/10._wp
         call evaluate_partial(u,v,0_ip,0_ip,computed(1))
         call evaluate_partial(u,v,1_ip,0_ip,computed(2))
         call evaluate_partial(u,v,0_ip,1_ip,computed(3))
         call evaluate_partial(u,v,1_ip,1_ip,computed(4))
         expected=[polynomial(u,v),2._wp*u+3._wp*u**2*v-v**3+u*v**2, &
            4._wp*v+u**3-3._wp*u*v**2+u**2*v,3._wp*u**2-3._wp*v**2+2._wp*u*v]
         polynomial_errors=max(polynomial_errors,abs(computed-expected)/max(1._wp,abs(expected)))
      end do
   end do
   if (maxval(polynomial_errors)>1.e-10_wp) error stop 'bicubic value or partial derivative mismatch'
   print '(a,i0)', 'Bicubic value/partial evaluations=',calls
   print '(a,4es13.4)', 'Scaled polynomial errors (value, dx, dy, dxdy):',polynomial_errors
   call interpolator%destroy()
   print '(a)', 'PASS bspline-tensor-surface'
contains
   subroutine evaluate(u,v,z)
      real(wp), intent(in) :: u,v
      real(wp), intent(out) :: z
      call evaluate_partial(u,v,0_ip,0_ip,z)
   end subroutine
   subroutine evaluate_partial(u,v,dx,dy,z)
      real(wp), intent(in) :: u,v
      integer(ip), intent(in) :: dx,dy
      real(wp), intent(out) :: z
      calls=calls+1
      call interpolator%evaluate(u,v,dx,dy,z,status)
      if (status/=0.or..not.ieee_is_finite(z)) error stop 'B-spline surface evaluation'
   end subroutine
   elemental real(wp) function polynomial(u,v) result(z)
      real(wp), intent(in) :: u,v
      z=1._wp+u**2+2._wp*v**2+u**3*v-u*v**3+0.5_wp*u**2*v**2
   end function
   elemental real(wp) function surface(u,v) result(z)
      real(wp), intent(in) :: u,v
      z=1._wp+2._wp*u-3._wp*v+0.5_wp*u*v
   end function
end program
