! Three unit masses and four unit springs, with both ends fixed.
program demo_foreig
   use kinds, only: rk
   use foreig, only: eig
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   real(rk) :: stiffness(3,3),workspace(3,3),identity(3,3),expected(3),residual,orthogonality
   real(rk), allocatable :: vectors(:,:),values(:)
   integer :: i
   stiffness = reshape([2.0_rk,-1.0_rk,0.0_rk,-1.0_rk,2.0_rk,-1.0_rk,0.0_rk,-1.0_rk,2.0_rk],[3,3])
   workspace = stiffness
   call eig(workspace,vectors,values,method='syev')
   if (.not. all(ieee_is_finite(values))) error stop 'Nonfinite eigenvalues'
   if (.not. all(ieee_is_finite(vectors))) error stop 'Nonfinite eigenvectors'
   identity = 0
   do i=1,3
      identity(i,i) = 1
      expected(i) = 2.0_rk-2.0_rk*cos(real(i,rk)*acos(-1.0_rk)/4.0_rk)
      residual = norm2(matmul(stiffness,vectors(:,i))-values(i)*vectors(:,i))
      if (residual>1e-11_rk) error stop 'Eigenpair residual too large'
   end do
   orthogonality = maxval(abs(matmul(transpose(vectors),vectors)-identity))
   if (orthogonality>1e-11_rk) error stop 'Eigenvectors are not orthonormal'
   if (maxval(abs(values-expected))>1e-11_rk) error stop 'Analytic eigenvalues differ'
   print '(a)', 'Mode    Squared angular frequency    Angular frequency'
   do i=1,3
      print '(i3,2f25.12)',i,values(i),sqrt(values(i))
   end do
   print '(a,es12.3)', 'Orthogonality error: ',orthogonality
   print '(a)', 'PASS foreig'
end program
