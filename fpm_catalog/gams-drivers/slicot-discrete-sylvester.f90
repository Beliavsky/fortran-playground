! Author API patterns adapted on 2026-10-30: constructed known matrix solutions and residual checks.
! Copyright (c) 1996-2026, The SLICOT Team
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
program checked_sylvester_equation
   use iso_fortran_env, only: wp=>real64
   use slicot, only: sb04qd
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer, parameter :: n=2,m=3,lwork=1000
   real(wp) :: original_a(n,n),original_b(m,m),a(n,n),b(m,m),known(n,m),rhs(n,m),c(n,m),z(m,m)
   real(wp) :: work(lwork),residual_matrix(n,m),error,residual
   integer :: problem,i,info,iwork(4*n)
   original_a=reshape([0.2_wp,0._wp,0.1_wp,0.4_wp],[n,n])
   original_b=reshape([0.3_wp,0._wp,0._wp,-0.2_wp,0.5_wp,0._wp,0._wp,0.1_wp,0.6_wp],[m,m])
   do problem=1,2
      if (problem==1) then
         a=original_a;b=original_b
         known=reshape([1._wp,3._wp,-2._wp,1._wp,0.5_wp,-1._wp],[n,m])
      else
         a=transpose(original_a);b=transpose(original_b)
         known=reshape([-1._wp,0.5_wp,0._wp,-2._wp,2._wp,1._wp],[n,m])
      end if
      rhs=known+matmul(a,matmul(known,b))
      c=rhs
      call sb04qd(n,m,a,n,b,m,c,n,z,m,iwork,work,lwork,info)
      if (info/=0) error stop 'Sylvester solver did not report success'
      if (.not.all(ieee_is_finite(c))) error stop 'nonfinite Sylvester solution'
      ! The solver overwrites A and B; reconstruct the original coefficients for the residual.
      if (problem==1) then
         a=original_a;b=original_b
      else
         a=transpose(original_a);b=transpose(original_b)
      end if
      residual_matrix=c+matmul(a,matmul(c,b))-rhs
      error=maxval(abs(c-known))/max(1._wp,maxval(abs(known)))
      residual=maxval(abs(residual_matrix))/max(1._wp,maxval(abs(rhs)))
      if (.not.ieee_is_finite(residual)) error stop 'nonfinite Sylvester residual'
      if (error>1.e-10_wp.or.residual>1.e-12_wp) error stop 'known Sylvester matrix or residual mismatch'
      print '(a,i0)', 'Rectangular Sylvester case ',problem
      print '(a,2es13.4)', 'Scaled solution error / residual:',error,residual
      print '(a)', 'Recovered 2-by-3 solution:'
      do i=1,n
         print '(3f14.8)',c(i,:)
      end do
   end do
   print '(a)', 'PASS slicot-discrete-sylvester'
end program
