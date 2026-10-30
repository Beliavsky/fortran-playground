! Adapted author API examples; shared deterministic problems and independent checks.
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
program checked_linear_algebra
   use iso_fortran_env, only: wp=>real64
   use ieee_arithmetic, only: ieee_is_finite
   use linear_algebra, only: lstsq
   use la_state_type, only: la_state
   use la_constants, only: ilp
   implicit none
   type(la_state) :: state
   real(wp), parameter :: t(5)=[-2._wp,-1._wp,0._wp,1._wp,2._wp]
   real(wp), parameter :: noise(5)=[1._wp,-2._wp,2._wp,-2._wp,1._wp]
   real(wp), allocatable :: a(:,:),original(:,:),x(:),expected(:)
   real(wp) :: b(5),rhs(5),residual(5),coefficient_error,optimality,sse
   integer(ilp) :: rank
   integer :: problem,n
   do problem=1,2
      ! Noise is orthogonal to both columns, giving known least-squares coefficients.
      n=problem+1
      allocate(a(5,n),expected(n))
      a(:,1)=1._wp; a(:,2)=t
      if (problem==1) then
         expected=[1._wp,2._wp]
      else
         ! Duplicate columns: infinitely many solutions; [1,1,1] has minimum norm.
         a(:,3)=t
         expected=[1._wp,1._wp,1._wp]
      end if
      b=1._wp+2._wp*t+noise
      original=a; rhs=b
      x=lstsq(a,b,rank=rank,err=state)
      if (state%error()) then
         print *, state%print()
         error stop 'least-squares solver status'
      end if
      if (size(x)/=n.or.rank/=2) error stop 'solution shape or numerical rank'
      if (.not.all(ieee_is_finite(x))) error stop 'nonfinite coefficients'
      residual=matmul(original,x)-rhs
      coefficient_error=maxval(abs(x-expected))
      optimality=maxval(abs(matmul(transpose(original),residual)))
      sse=sum(residual**2)
      if (coefficient_error>1.e-10_wp.or.optimality>1.e-10_wp) error stop 'least-squares optimality'
      if (abs(sse-14._wp)>1.e-10_wp) error stop 'least-squares residual sum of squares'
      print '(a,i0)', 'Least-squares case (2 has duplicate columns): ', problem
      print '(a,*(f18.12))', 'Coefficients: ', x
      print '(a,i0)', 'Numerical rank: ', rank
      print '(a,es12.4)', 'Maximum coefficient error: ', coefficient_error
      print '(a,es12.4)', 'Maximum absolute A-transpose residual: ', optimality
      print '(a,f18.12)', 'Residual sum of squares (expected 14): ', sse
      deallocate(a,expected)
   end do
   print '(a)', 'PASS fortran-lapack-least-squares'
end program
