! A rank-one matrix needs an explicit singular-value cutoff in this API.
program demo_forinv
   use kinds, only: rk
   use forinv, only: inv
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   real(rk) :: a(3,2),workspace(3,2),pinv(2,3),b(3),x(2),left(3,3),right(2,2),errors(4)
   integer :: i
   a(:,1) = [1.0_rk,2.0_rk,3.0_rk]
   a(:,2) = 2*a(:,1)
   b = a(:,1)
   ! The pinned ForSVD passes its input to LAPACK workspace despite INTENT(IN).
   ! Preserve the original matrix explicitly for residuals and later use.
   workspace = a
   pinv = inv(workspace,tol=1e-10_rk)
   if (.not. all(ieee_is_finite(pinv))) error stop 'Nonfinite pseudoinverse'
   left = matmul(a,pinv); right = matmul(pinv,a)
   errors = [maxval(abs(matmul(left,a)-a)),maxval(abs(matmul(right,pinv)-pinv)), &
      maxval(abs(transpose(left)-left)),maxval(abs(transpose(right)-right))]
   if (any(errors>1e-11_rk)) error stop 'Moore-Penrose identities fail'
   x = matmul(pinv,b)
   ! All solutions satisfy x1+2*x2=1; the minimum-norm one is (1/5,2/5).
   if (maxval(abs(x-[0.2_rk,0.4_rk]))>1e-11_rk) error stop 'Wrong minimum-norm solution'
   if (maxval(abs(matmul(a,x)-b))>1e-11_rk) error stop 'Residual too large'
   print '(a)', 'Pseudoinverse of a rank-deficient 3 by 2 matrix:'
   do i=1,2
      print '(3f14.8)',pinv(i,:)
   end do
   print '(a,2f14.8)', 'Minimum-norm solution: ',x
   print '(a,4es12.3)', 'Four Moore-Penrose identity errors: ',errors
   print '(a)', 'PASS forinv'
end program
