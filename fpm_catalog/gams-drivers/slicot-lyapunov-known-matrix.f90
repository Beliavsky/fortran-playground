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
program checked_lyapunov_equations
   use iso_fortran_env, only: wp=>real64
   use slicot, only: sb03md
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer, parameter :: n=3,lwork=1000
   real(wp), parameter :: base(n,n)=reshape([2._wp,0.5_wp,-0.25_wp, &
      0.5_wp,1._wp,0.2_wp,-0.25_wp,0.2_wp,1.5_wp],[n,n])
   real(wp) :: original(n,n),op(n,n),a(n,n),u(n,n),c(n,n),rhs(n,n),known(n,n),residual_matrix(n,n),solution(n,n)
   real(wp) :: scale,sep,ferr,wr(n),wi(n),work(lwork),error,residual,symmetry
   integer :: equation,trans,rhs_number,i,info,iwork(n*n)
   character :: dico,trana,fact
   do equation=1,2
      if (equation==1) then
         dico='C'
         original=reshape([-1._wp,-2._wp,0._wp,2._wp,-1._wp,0._wp,0._wp,0.5_wp,-3._wp],[n,n])
      else
         dico='D'
         original=reshape([0.2_wp,-0.3_wp,0._wp,0.3_wp,0.2_wp,0._wp,0._wp,0.1_wp,0.5_wp],[n,n])
      end if
      do trans=1,2
         if (trans==1) then
            trana='N';op=original
         else
            trana='T';op=transpose(original)
         end if
         a=original
         do rhs_number=1,2
            if (rhs_number==1) then
               fact='N';known=base
            else
               ! Retain A in Schur form and U from the previous solve; replace only the RHS.
               fact='F';known=0.5_wp*base
               do i=1,n
                  known(i,i)=known(i,i)+1._wp
               end do
            end if
            if (dico=='C') then
               rhs=matmul(transpose(op),known)+matmul(known,op)
            else
               rhs=matmul(transpose(op),matmul(known,op))-known
            end if
            c=rhs
            call sb03md(dico,'X',fact,trana,n,a,n,u,n,c,n,scale,sep,ferr,wr,wi,iwork,work,lwork,info)
            if (info/=0) error stop 'Lyapunov solver did not report success'
            if (.not.ieee_is_finite(scale)) error stop 'nonfinite scale'
            if (scale<=0._wp.or.scale>1._wp) error stop 'invalid scale'
            solution=c/scale
            if (.not.all(ieee_is_finite(solution))) error stop 'nonfinite Lyapunov solution'
            if (dico=='C') then
               residual_matrix=matmul(transpose(op),c)+matmul(c,op)-scale*rhs
            else
               residual_matrix=matmul(transpose(op),matmul(c,op))-c-scale*rhs
            end if
            error=maxval(abs(solution-known))/max(1._wp,maxval(abs(known)))
            residual=maxval(abs(residual_matrix))/max(1._wp,maxval(abs(scale*rhs)))
            symmetry=maxval(abs(solution-transpose(solution)))
            if (.not.ieee_is_finite(residual)) error stop 'nonfinite Lyapunov residual'
            if (error>1.e-10_wp.or.residual>1.e-12_wp.or.symmetry>1.e-12_wp) &
               error stop 'known Lyapunov matrix or residual mismatch'
            print '(a,a,a,a,a,a,a,i0)', 'DICO=',dico,' TRANA=',trana,' FACT=',fact,' RHS=',rhs_number
            print '(a,4es13.4)', 'Scale / solution error / residual / symmetry:',scale,error,residual,symmetry
         end do
      end do
   end do
   print '(a)', 'PASS slicot-lyapunov-known-matrix'
end program
