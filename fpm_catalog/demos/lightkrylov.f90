program main
   use LightKrylov, only: dense_linop_rdp, dense_vector_rdp, dense_vector, gmres
   use LightKrylov_Constants, only: dp
   implicit none
   type(dense_linop_rdp) :: operator
   type(dense_vector_rdp) :: rhs, solution
   real(dp) :: matrix(6,6), expected(6), residual
   integer :: i, info
   matrix=0._dp; expected=1._dp
   do i=1,6
      matrix(i,i)=real(i,dp)
      if (i<6) matrix(i,i+1)=0.25_dp
   end do
   operator%data=matrix
   rhs=dense_vector(matmul(matrix,expected))
   solution=dense_vector([0._dp,0._dp,0._dp,0._dp,0._dp,0._dp])
   ! GMRES uses the operator's matrix-vector action to solve A*x = b.
   call gmres(operator,rhs,solution,info,rtol=1.e-10_dp,atol=1.e-12_dp)
   if (info<0) error stop 'GMRES failed'
   residual=sqrt(sum((matmul(matrix,solution%data)-rhs%data)**2))
   if (residual>1.e-8_dp) error stop 'large linear-system residual'
   if (maxval(abs(solution%data-expected))>1.e-8_dp) error stop 'incorrect solution'
   print *, 'GMRES solution:',solution%data
   print *, 'Residual norm:',residual
   print *, 'PASS lightkrylov'
end program main
