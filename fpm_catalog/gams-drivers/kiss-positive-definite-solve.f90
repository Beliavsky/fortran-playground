! Adapted author solver API patterns; deterministic solution and residual checks.
! BSD 3-Clause License
! 
! Copyright (c) 2025, Ivan Pribec
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
program checked_positive_definite_solve
   use kiss, only: wp,cg_dense
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer, parameter :: n=20
   real(wp) :: a(n,n),exact(n),b(n),x(n),error,residual,backward
   integer :: i,rhs,status
   a=0._wp
   do i=1,n
      a(i,i)=4._wp
      if (i<n) then
         a(i,i+1)=-1._wp
         a(i+1,i)=-1._wp
      end if
   end do
   ! Strict symmetric diagonal dominance with positive diagonal implies positive definiteness.
   do rhs=1,2
      do i=1,n
         if (rhs==1) then
            exact(i)=real(i,wp)/n
         else
            exact(i)=(-1._wp)**i
         end if
      end do
      ! Construct b with the stencil, independently of dense MATMUL.
      b=4._wp*exact
      b(2:n)=b(2:n)-exact(1:n-1)
      b(1:n-1)=b(1:n-1)-exact(2:n)
      x=0._wp
      call cg_dense(a,b,x,rtol=1.e-12_wp,atol=1.e-14_wp,maxiter=200,info=status)
      if (status/=0) error stop 'conjugate gradient did not report convergence'
      if (.not.all(ieee_is_finite(x))) error stop 'nonfinite solution'
      error=maxval(abs(x-exact))
      residual=maxval(abs(matmul(a,x)-b))
      backward=residual/(maxval(sum(abs(a),dim=2))*maxval(abs(x))+maxval(abs(b)))
      if (.not.ieee_is_finite(backward)) error stop 'nonfinite backward error'
      if (error>1.e-9_wp.or.backward>1.e-11_wp) error stop 'solution or backward error mismatch'
      print '(a,i0,a,i0)', 'RHS ',rhs,' status=',status
      print '(a,5f12.7)', 'First five solution entries:',x(1:5)
      print '(a,3es13.4)', 'Max solution error / residual / scaled backward error:',error,residual,backward
   end do
   print '(a)', 'PASS kiss-positive-definite-solve'
end program
