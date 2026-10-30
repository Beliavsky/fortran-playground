! Adapted author API examples; shared deterministic problems and independent checks.
! MIT License
! 
! Copyright (c) 2019-2021 stdlib contributors
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
program checked_linear_algebra
   use iso_fortran_env, only: wp=>real64
   use ieee_arithmetic, only: ieee_is_finite
   use stdlib_linalg, only: lstsq, linalg_state_type
   use stdlib_linalg_constants, only: ilp
   implicit none
   type(linalg_state_type) :: state
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
   print '(a)', 'PASS stdlib-least-squares'
end program
