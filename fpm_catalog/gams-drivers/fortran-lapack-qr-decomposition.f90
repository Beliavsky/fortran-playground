! Adapted author decomposition API pattern; deterministic matrices and independent checks.
! BSD 3-Clause License
! 
! Copyright (c) 2024, Federico Perini
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
program checked_decomposition
   use iso_fortran_env, only: wp=>real64
   use ieee_arithmetic, only: ieee_is_finite
   use linear_algebra, only: qr
   use la_state_type, only: la_state
   implicit none
   type(la_state) :: state
   real(wp) :: identity(3,3),scale,reconstruction_error,orthogonality_error
   integer :: problem,j
   real(wp), parameter :: t(4)=[-1._wp,0._wp,1._wp,2._wp]
   real(wp) :: a(4,3),original(4,3),q(4,3),r(3,3),triangle_error
   real(wp) :: b(4),rhs(3),coefficients(3),expected(3),residual(4),optimality,sse
   integer :: k
   identity=0._wp
   do j=1,3
      identity(j,j)=1._wp
   end do
   do problem=1,2
      a(:,1)=1._wp; a(:,2)=t; a(:,3)=t*t
      if (problem==2) a(:,3)=2._wp*t ! Known dependent column.
      original=a
      call qr(a,q,r,err=state)
      if (state%error()) then
         print *,state%print()
         error stop 'QR factorization status'
      end if
      if (.not.all(ieee_is_finite(q)).or..not.all(ieee_is_finite(r))) error stop 'nonfinite QR factors'
      scale=max(1._wp,sqrt(sum(original**2)))
      reconstruction_error=sqrt(sum((matmul(q,r)-original)**2))/scale
      orthogonality_error=sqrt(sum((matmul(transpose(q),q)-identity)**2))
      triangle_error=0._wp
      do j=1,3
         do k=1,j-1
            triangle_error=max(triangle_error,abs(r(j,k)))
         end do
      end do
      if (max(reconstruction_error,orthogonality_error,triangle_error)>1.e-12_wp) error stop 'QR identities'
      print '(a,i0)', 'Reduced QR case (2 has dependent columns): ',problem
      print '(a,es12.4)', 'Maximum lower-triangular R entry: ',triangle_error
      if (problem==1) then
         ! Noise [-1,3,-3,1]/10 is orthogonal to columns [1,t,t**2].
         expected=[1._wp,-2._wp,0.5_wp]
         b=matmul(original,expected)+[-0.1_wp,0.3_wp,-0.3_wp,0.1_wp]
         rhs=matmul(transpose(q),b)
         coefficients=0._wp
         do j=3,1,-1
            if (abs(r(j,j))<1.e-12_wp) error stop 'unexpected rank loss'
            coefficients(j)=(rhs(j)-dot_product(r(j,j+1:3),coefficients(j+1:3)))/r(j,j)
         end do
         residual=matmul(original,coefficients)-b
         optimality=maxval(abs(matmul(transpose(original),residual)))
         sse=sum(residual**2)
         if (maxval(abs(coefficients-expected))>1.e-12_wp.or.optimality>1.e-12_wp) &
            error stop 'QR least-squares coefficients/optimality'
         if (abs(sse-0.2_wp)>1.e-12_wp) error stop 'QR least-squares residual norm'
         print '(a,3f18.12)', 'Least-squares coefficients: ',coefficients
         print '(a,es12.4)', 'Maximum absolute A-transpose residual: ',optimality
         print '(a,f18.12)', 'Residual sum of squares (expected 0.2): ',sse
      else
         if (abs(r(3,3))/scale>1.e-12_wp) error stop 'known dependent QR column'
         print '(a)', 'Dependent column detected; triangular solve skipped.'
      end if
      print '(a,es12.4)', 'Relative Frobenius reconstruction error: ',reconstruction_error
      print '(a,es12.4)', 'Column orthogonality error: ',orthogonality_error
   end do
   print '(a)', 'PASS fortran-lapack-qr-decomposition'
end program
