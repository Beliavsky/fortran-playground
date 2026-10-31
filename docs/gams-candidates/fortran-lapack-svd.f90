! Hosted link-limit reproducer, not a verified menu example.
! Observed with GNU 16.2.0/FPM 0.12.0 and the 16 MiB per-file limit.
! Package revision: e5e45fdd5a38bfab06d1f703f12b787937aa33bb
! The working menu example uses the lower-level GESVD API; see ../gams-linear-algebra.md.
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
   use linear_algebra, only: svd
   use la_state_type, only: la_state
   implicit none
   type(la_state) :: state
   real(wp) :: identity(3,3),scale,reconstruction_error,orthogonality_error
   integer :: problem,j
   real(wp) :: a(4,3),original(4,3),u(4,3),vt(3,3),singular(3),expected(3),weighted(4,3)
   real(wp) :: right_orthogonality_error,rank_threshold
   integer :: numerical_rank
   identity=0._wp
   do j=1,3
      identity(j,j)=1._wp
   end do
   do problem=1,2
      ! The first block has singular values 3 and 0; the third column adds 2.
      a=0._wp
      a(1:2,1:2)=1.5_wp; a(3,3)=2._wp
      expected=[3._wp,2._wp,0._wp]
      if (problem==2) then
         a(4,:)=[1._wp,-1._wp,0._wp]
         expected(3)=sqrt(2._wp)
      end if
      original=a
      call svd(a,singular,u,vt,full_matrices=.false.,err=state)
      if (state%error()) then
         print *,state%print()
         error stop 'SVD status'
      end if
      if (.not.all(ieee_is_finite(singular)).or..not.all(ieee_is_finite(u)).or. &
          .not.all(ieee_is_finite(vt))) error stop 'nonfinite SVD'
      if (any(singular<0._wp).or.any(singular(1:2)<singular(2:3))) error stop 'singular value ordering'
      do j=1,3
         weighted(:,j)=u(:,j)*singular(j)
      end do
      scale=max(1._wp,sqrt(sum(original**2)))
      reconstruction_error=sqrt(sum((matmul(weighted,vt)-original)**2))/scale
      orthogonality_error=sqrt(sum((matmul(transpose(u),u)-identity)**2))
      right_orthogonality_error=sqrt(sum((matmul(vt,transpose(vt))-identity)**2))
      if (maxval(abs(singular-expected))>1.e-12_wp) error stop 'known singular values'
      if (max(reconstruction_error,orthogonality_error,right_orthogonality_error)>1.e-12_wp) &
         error stop 'SVD identities'
      rank_threshold=4._wp*epsilon(1._wp)*maxval(singular)
      numerical_rank=count(singular>rank_threshold)
      if (numerical_rank/=problem+1) error stop 'known numerical rank'
      print '(a,i0)', 'Reduced SVD case (1 has rank 2; 2 has rank 3): ',problem
      print '(a,3f18.12)', 'Singular values: ',singular
      print '(a,i0)', 'Numerical rank: ',numerical_rank
      print '(a,es12.4)', 'Right-factor orthogonality error: ',right_orthogonality_error
      print '(a,es12.4)', 'Relative Frobenius reconstruction error: ',reconstruction_error
      print '(a,es12.4)', 'Column orthogonality error: ',orthogonality_error
   end do
   print '(a)', 'PASS fortran-lapack-svd-decomposition'
end program
