! Adapted author transform API examples; deterministic data and direct-sum checks.
! BSD 3-Clause License
! 
! Copyright (c) 2023, 左志华（zuo.zhihua@qq.com）
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
program checked_transform
   use ieee_arithmetic, only: ieee_is_finite
   use iso_fortran_env, only: wp=>real64
   use iso_c_binding, only: c_associated,c_float
   use kissfft, only: fft,kiss_fft_cpx
   implicit none
   integer :: test,n,j,k
   real(wp) :: pi,angle,forward_error,roundtrip_error
   complex(wp), allocatable :: signal(:),spectrum(:),reference(:),restored(:)
   real(wp) :: energy_error
   pi=acos(-1._wp)
   do test=1,2
      n=6+test
      allocate(signal(n),reference(n),spectrum(n),restored(n))
      do j=0,n-1
         signal(j+1)=cmplx(real(j+1,wp)/8._wp,real((-1)**j,wp)/4._wp,wp)
      end do
      ! Independent O(N**2) DFT reference, using the negative-exponent convention.
      reference=cmplx(0._wp,0._wp,wp)
      do k=0,n-1
         do j=0,n-1
            angle=-2._wp*pi*real(j*k,wp)/real(n,wp)
            reference(k+1)=reference(k+1)+signal(j+1)*cmplx(cos(angle),sin(angle),wp)
         end do
      end do
      block
         ! Each plan is initialized once; block exit finalizes and frees both plans.
         type(fft) :: forward,inverse
         type(kiss_fft_cpx) :: input(n),output(n),back(n)
         input%re=real(signal,c_float); input%im=real(aimag(signal),c_float)
         call forward%init(n,0)
         call inverse%init(n,1)
         if (.not.c_associated(forward%kiss_fft_cfg).or..not.c_associated(inverse%kiss_fft_cfg)) &
            error stop 'KISS FFT plan allocation'
         call forward%perform(input,output)
         spectrum=cmplx(output%re,output%im,wp)
         call inverse%perform(output,back)
         restored=cmplx(back%re,back%im,wp)/real(n,wp)
      end block
      if (.not.all(ieee_is_finite(real(spectrum))).or..not.all(ieee_is_finite(aimag(spectrum)))) &
         error stop 'nonfinite forward FFT'
      if (.not.all(ieee_is_finite(real(restored))).or..not.all(ieee_is_finite(aimag(restored)))) &
         error stop 'nonfinite inverse FFT'
      energy_error=abs(sum(abs(spectrum)**2)/real(n,wp)-sum(abs(signal)**2))/max(1._wp,sum(abs(signal)**2))
      if (energy_error>1.e-6_wp) error stop 'Parseval energy identity'
      forward_error=maxval(abs(spectrum-reference))
      roundtrip_error=maxval(abs(restored-signal))
      if (forward_error>1.e-5_wp.or.roundtrip_error>1.e-6_wp) &
         error stop 'direct reference or round-trip accuracy'
      print '(a,i0)', 'Transform length: ',n
      print '(a,es12.4)', 'Maximum forward error against direct sum: ',forward_error
      print '(a,es12.4)', 'Maximum normalized inverse error: ',roundtrip_error
      print '(a,es12.4)', 'Relative Parseval energy error: ',energy_error
      deallocate(signal,reference,spectrum,restored)
   end do
   print '(a)', 'PASS kissfft-f-complex-transform'
end program
