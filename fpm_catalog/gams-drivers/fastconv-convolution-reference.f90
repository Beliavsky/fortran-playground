! Author API patterns adapted on 2026-10-30: independent direct-sum convolution checks.
! BSD 3-Clause License
! 
! Copyright (c) 2024, Dominik Gronkiewicz
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
module direct_convolution
   use iso_fortran_env, only: wp=>real64,sp=>real32
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
contains
   function full_reference(x,h) result(y)
      real(wp), intent(in) :: x(:),h(:)
      real(wp) :: y(size(x)+size(h)-1)
      integer :: i,j
      y=0._wp
      do j=1,size(h)
         do i=1,size(x)
            y(i+j-1)=y(i+j-1)+x(i)*h(j)
         end do
      end do
   end function
   subroutine check(y,reference,tolerance,error)
      real(wp), intent(in) :: y(:),reference(:),tolerance
      real(wp), intent(out) :: error
      if (size(y)/=size(reference)) error stop 'convolution output length mismatch'
      if (.not.all(ieee_is_finite(y))) error stop 'nonfinite convolution output'
      error=maxval(abs(y-reference))/max(1._wp,maxval(abs(reference)))
      if (error>tolerance) error stop 'direct convolution reference mismatch'
   end subroutine
end module
program checked_convolution
   use direct_convolution
   use conv1d_m, only: conv1d_t
   implicit none
   integer, parameter :: n=37,lengths(8)=[1,2,3,4,5,8,16,17]
   real(wp) :: x(n),error
   real(wp), allocatable :: h(:),full(:)
   type(conv1d_t) :: filter
   real(sp) :: native_x(n)
   real(sp), allocatable :: native_h(:),native_y(:)
   integer :: signal,choice,m,i
   do signal=1,2
      if (signal==1) then
         x=0._wp;x(10)=1._wp
      else
         do i=1,n
            x(i)=sin(0.2_wp*i)+(-1._wp)**i*0.1_wp*i
         end do
      end if
      do choice=1,size(lengths)
         m=lengths(choice)
         allocate(h(m))
         do i=1,m
            h(i)=(-1._wp)**i/real(i+1,wp)
         end do
         if (m==1) h=1._wp
         native_x=real(x,sp);native_h=real(h,sp)
         call filter%set_kernel(native_h)
         filter%preserve_shape=.false.
         native_y=filter%apply(native_x)
         ! Accumulate in real64 using the actual real32 inputs passed to fastconv.
         full=full_reference(real(native_x,wp),real(native_h,wp))
         call check(real(native_y,wp),full(m:n),2.e-6_wp,error)
         print '(a,i0,a,i0,a,i0,a,es12.3)', 'Signal ',signal,' kernel ',m, &
            ' valid length=',size(native_y),' scaled direct-reference error=',error

         deallocate(h)
      end do
   end do
   print '(a)', 'PASS fastconv-convolution-reference'
end program
