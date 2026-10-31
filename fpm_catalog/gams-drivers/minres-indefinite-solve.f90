! Adapted author solver API patterns; deterministic solution and residual checks.
! The MIT License (MIT)
! ---------------------
! 
! Copyright © 2022  IO Rodeo
! 
! Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
! documentation files (the “Software”), to deal in the Software without restriction, including without limitation the
! rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
! persons to whom the Software is furnished to do so, subject to the following conditions:
! 
! The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
! Software.
! 
! THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
! WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
! COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
! OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
module sparse_equations
   use iso_fortran_env, only: wp=>real64
   implicit none
   integer, parameter :: row(11)=[1,1,2,2,3,1,2,3,4,3,5],col(11)=[1,2,2,3,3,4,4,4,4,5,5]
   real(wp), parameter :: entries(11)=[4._wp,1._wp,5._wp,-1._wp,6._wp,1._wp,2._wp,-1._wp,-2._wp,1._wp,-3._wp]
contains
   subroutine aprod(n,x,y)
      integer, intent(in) :: n
      real(wp), intent(in) :: x(n)
      real(wp), intent(out) :: y(n)
      integer :: k
      y=0._wp
      do k=1,size(entries)
         y(row(k))=y(row(k))+entries(k)*x(col(k))
         if (row(k)/=col(k)) y(col(k))=y(col(k))+entries(k)*x(row(k))
      end do
   end subroutine
   subroutine identity(n,x,y)
      integer, intent(in) :: n
      real(wp), intent(in) :: x(n)
      real(wp), intent(out) :: y(n)
      y=x
   end subroutine
end module
program checked_sparse_solve
   use sparse_equations
   use minres, only: minres_solver
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
   real(wp), parameter :: a(5,5)=reshape([ &
      4._wp,1._wp,0._wp,1._wp,0._wp, &
      1._wp,5._wp,-1._wp,2._wp,0._wp, &
      0._wp,-1._wp,6._wp,-1._wp,1._wp, &
      1._wp,2._wp,-1._wp,-2._wp,0._wp, &
      0._wp,0._wp,1._wp,0._wp,-3._wp],[5,5],order=[2,1])
   real(wp), parameter :: exact(5,2)=reshape([1._wp,-2._wp,3._wp,-1._wp,2._wp, &
      -1._wp,0.5_wp,2._wp,1._wp,-2._wp],[5,2])
   real(wp) :: b(5),x(5),anorm,acond,rnorm,arnorm,ynorm,error,residual,backward,ax(5)
   integer :: rhs,stop_reason,iterations
   do rhs=1,2
      b=matmul(a,exact(:,rhs))
      ! Matrix-vector callback uses upper-coordinate storage; reference uses explicit dense A.
      call aprod(5,exact(:,rhs),ax)
      if (maxval(abs(ax-b))>1.e-13_wp) error stop 'operator does not match reference matrix'
      call minres_solver(5,aprod,identity,b,0._wp,.true.,.false.,x,100,0,1.e-12_wp, &
         stop_reason,iterations,anorm,acond,rnorm,arnorm,ynorm)
      if (stop_reason/=1.and.stop_reason/=2) error stop 'MINRES did not report residual convergence'
      if (.not.all(ieee_is_finite(x))) error stop 'nonfinite solution'
      error=maxval(abs(x-exact(:,rhs)))
      residual=maxval(abs(matmul(a,x)-b))
      backward=residual/(maxval(sum(abs(a),dim=2))*maxval(abs(x))+maxval(abs(b)))
      if (.not.ieee_is_finite(backward)) error stop 'nonfinite backward error'
      if (error>1.e-9_wp.or.backward>1.e-11_wp) error stop 'solution or backward error mismatch'
      print '(a,i0,a,i0,a,i0)', 'RHS ',rhs,' stop=',stop_reason,' iterations=',iterations
      print '(a,5f12.7)', 'Solution:',x
      print '(a,3es13.4)', 'Max solution error / residual / scaled backward error:',error,residual,backward
   end do
   print '(a)', 'PASS minres-indefinite-solve'
end program
