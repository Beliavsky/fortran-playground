! Original lower-level LAPACK API driver; deterministic matrices and independent checks.
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
   use la_lapack, only: syev
   implicit none
   integer :: info,lwork
   real(wp) :: query_work(1)
   real(wp), allocatable :: work(:)
   real(wp) :: identity(3,3),scale,reconstruction_error,orthogonality_error
   integer :: problem,j
   real(wp) :: a(3,3),original(3,3),vectors(3,3),eigenvalues(3),expected(3),weighted(3,3),equation_error
   identity=0._wp
   do j=1,3
      identity(j,j)=1._wp
   end do
   do problem=1,2
      ! A 2-by-2 symmetric block has eigenvalues 1 and 3.
      a=reshape([2._wp,1._wp,0._wp,1._wp,2._wp,0._wp,0._wp,0._wp,4._wp],[3,3])
      if (problem==2) a(3,3)=3._wp ! Repeated eigenvalue: its basis is not unique.
      expected=[1._wp,3._wp,a(3,3)]
      original=a
      call syev('V','U',3,a,3,eigenvalues,query_work,-1,info)
      if (info/=0.or..not.ieee_is_finite(query_work(1))) error stop 'SYEV workspace query'
      lwork=max(1,ceiling(query_work(1))); allocate(work(lwork))
      a=original
      call syev('V','U',3,a,3,eigenvalues,work,lwork,info)
      deallocate(work)
      if (info/=0) error stop 'SYEV status'
      vectors=a
      if (.not.all(ieee_is_finite(eigenvalues)).or..not.all(ieee_is_finite(vectors))) &
         error stop 'nonfinite eigensystem'
      do j=1,3
         weighted(:,j)=vectors(:,j)*eigenvalues(j)
      end do
      scale=max(1._wp,sqrt(sum(original**2)))
      equation_error=sqrt(sum((matmul(original,vectors)-weighted)**2))/scale
      reconstruction_error=sqrt(sum((matmul(weighted,transpose(vectors))-original)**2))/scale
      orthogonality_error=sqrt(sum((matmul(transpose(vectors),vectors)-identity)**2))
      if (maxval(abs(eigenvalues-expected))>1.e-12_wp) error stop 'known eigenvalues'
      if (max(equation_error,reconstruction_error,orthogonality_error)>1.e-12_wp) error stop 'eigen identities'
      print '(a,i0)', 'Symmetric eigenproblem case (2 has a repeated eigenvalue): ',problem
      print '(a,3f18.12)', 'Eigenvalues: ',eigenvalues
      print '(a,es12.4)', 'Relative Frobenius eigen-equation residual: ',equation_error
      print '(a,es12.4)', 'Relative Frobenius reconstruction error: ',reconstruction_error
      print '(a,es12.4)', 'Column orthogonality error: ',orthogonality_error
   end do
   print '(a)', 'PASS fortran-lapack-symmetric-eigen'
end program
