module sparse_operator
   use iso_fortran_env, only: dp=>real64
   implicit none
   integer, parameter :: row(7)=[1,2,3,2,3,1,2],col(7)=[1,2,3,1,2,2,3]
   real(dp), parameter :: entries(7)=[3._dp,2._dp,1._dp,4._dp,2._dp,4._dp,2._dp]
contains
   subroutine aprod(n,x,y)
      integer, intent(in) :: n
      real(dp), intent(in) :: x(n)
      real(dp), intent(out) :: y(n)
      integer :: i
      y=0._dp
      do i=1,size(entries)
         y(row(i))=y(row(i))+entries(i)*x(col(i))
      end do
   end subroutine
   subroutine msolve(n,x,y)
      integer, intent(in) :: n
      real(dp), intent(in) :: x(n)
      real(dp), intent(out) :: y(n)
      y=x
   end subroutine
end module
program main
   use sparse_operator
   use minres, only: minres_solver
   implicit none
   real(dp) :: b(3),x(3),ax(3),anorm,acond,rnorm,arnorm,ynorm,residual
   integer :: istop,itn
   call aprod(3,[1._dp,2._dp,3._dp],b)
   ! Module callbacks avoid the internal-procedure closures in minres_ez_t.
   call minres_solver(3,aprod,msolve,b,0._dp,.true.,.false.,x,100,0,1e-12_dp, &
      istop,itn,anorm,acond,rnorm,arnorm,ynorm)
   call aprod(3,x,ax)
   residual=maxval(abs(ax-b))
   if (residual>1e-9_dp.or.maxval(abs(x-[1._dp,2._dp,3._dp]))>1e-9_dp) error stop
   print '(a,3f12.7)', 'Solution:',x
   print '(a,i5)', 'Iterations:',itn
   print '(a,es12.4)', 'Maximum residual:',residual
   print *, 'PASS minres'
end program main
