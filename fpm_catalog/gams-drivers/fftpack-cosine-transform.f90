! Adapted author transform API examples; deterministic data and direct-sum checks.
! MIT License
! 
! Copyright (c) 2021-2023 fftpack Contributors
! 
! Permission is hereby granted, free of charge, to any person obtaining a copy
! of this software and associated documentation files (the "Software"), to deal
! in the Software without restriction, including without limitation the rights
! to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
! copies of the Software, and to permit persons to whom the Software is
! furnished to do so, subject to the following conditions:
! 
! The above copyright notice and this permission notice shall be included in all
! copies or substantial portions of the Software.
! 
! THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
! IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
! FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
! AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
! LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
! OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
! SOFTWARE.
! 
! The original Software this work is based on is in the Public Domain. All changes
! made and to be made to the original Software are covered by the MIT License.
program checked_transform
   use ieee_arithmetic, only: ieee_is_finite
   use fftpack, only: dct,idct,wp=>rk
   implicit none
   integer :: test,n,j,k
   real(wp) :: pi,angle,forward_error,roundtrip_error
   real(wp), allocatable :: signal(:),spectrum(:),reference(:),restored(:)
   pi=acos(-1._wp)
   do test=1,2
      n=6+test
      allocate(signal(n),reference(n),spectrum(n),restored(n))
      do j=0,n-1
         signal(j+1)=real(j+1,wp)/8._wp
      end do
      ! This API's DCT-II is 4*sum_j x(j)*cos(pi*(j+1/2)*k/N).
      reference=0._wp
      do k=0,n-1
         do j=0,n-1
            angle=pi*(real(j,wp)+0.5_wp)*real(k,wp)/real(n,wp)
            reference(k+1)=reference(k+1)+4._wp*signal(j+1)*cos(angle)
         end do
      end do
      spectrum=dct(signal,type=2)
      restored=idct(spectrum,type=2)/real(4*n,wp)
      if (.not.all(ieee_is_finite(spectrum)).or..not.all(ieee_is_finite(restored))) error stop 'nonfinite DCT'
      forward_error=maxval(abs(spectrum-reference))
      roundtrip_error=maxval(abs(restored-signal))
      if (forward_error>1.e-11_wp.or.roundtrip_error>1.e-11_wp) &
         error stop 'direct reference or round-trip accuracy'
      print '(a,i0)', 'Transform length: ',n
      print '(a,es12.4)', 'Maximum forward error against direct sum: ',forward_error
      print '(a,es12.4)', 'Maximum normalized inverse error: ',roundtrip_error
      deallocate(signal,reference,spectrum,restored)
   end do
   print '(a)', 'PASS fftpack-cosine-transform'
end program
