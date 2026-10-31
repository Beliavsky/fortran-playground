! Author API patterns adapted on 2026-10-30: checked nonuniform 2D surfaces.
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
program checked_surface_interpolation
   use iso_fortran_env, only: wp=>real64
   use linear_interpolation_module, only: linear_interp_2d
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer, parameter :: nx=6,ny=5
   real(wp), parameter :: x(nx)=[-1._wp,-0.6_wp,0._wp,0.3_wp,1._wp,2._wp]
   real(wp), parameter :: y(ny)=[-2._wp,-0.75_wp,0._wp,0.5_wp,1.5_wp]
   real(wp) :: f(nx,ny),u,v,s,t,answer,reference,node_error,formula_error,bounds_error,reproduction_error
   integer :: problem,i,j,ix,iy,calls
   type(linear_interp_2d) :: interpolator
   integer :: status
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
      call interpolator%initialize(x,y,f,status)
      if (status/=0) error stop '2D interpolator initialization'
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
   call interpolator%destroy()
   print '(a)', 'PASS finterp-bilinear-surface'
contains
   subroutine evaluate(u,v,z)
      real(wp), intent(in) :: u,v
      real(wp), intent(out) :: z
      calls=calls+1
      call interpolator%evaluate(u,v,z,status)
      if (status/=0.or..not.ieee_is_finite(z)) error stop '2D interpolation evaluation'
   end subroutine
   elemental real(wp) function surface(u,v) result(z)
      real(wp), intent(in) :: u,v
      z=1._wp+2._wp*u-3._wp*v+0.5_wp*u*v
   end function
end program
