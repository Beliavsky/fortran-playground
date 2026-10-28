program main
   use iso_fortran_env, only: dp=>real64
   use minres, only: minres_ez_t,minres_info_t
   implicit none
   type(minres_ez_t) :: solver
   type(minres_info_t) :: info
   integer, parameter :: row(7)=[1,2,3,2,3,1,2],col(7)=[1,2,3,1,2,2,3]
   real(dp), parameter :: entries(7)=[3._dp,2._dp,1._dp,4._dp,2._dp,4._dp,2._dp]
   real(dp) :: a(3,3),b(3),x(3),residual
   integer :: i
   a=0._dp
   do i=1,7
      a(row(i),col(i))=entries(i)
   end do
   b=matmul(a,[1._dp,2._dp,3._dp])
   solver%itnlim=100; solver%rtol=1e-12_dp
   solver%precon=.false.; solver%checka=.true.
   call solver%solve(row,col,entries,b,x,info)
   residual=maxval(abs(matmul(a,x)-b))
   if (residual>1e-9_dp.or.maxval(abs(x-[1._dp,2._dp,3._dp]))>1e-9_dp) error stop
   print '(a,3f12.7)', 'Solution:',x
   print '(a,es12.4)', 'Maximum residual:',residual
   print *, 'PASS minres'
end program main
