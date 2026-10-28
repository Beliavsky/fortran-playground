program demo_linalg
   use iso_fortran_env, only: real64, int32
   use linalg, only: lu_factor, solve_lu, eigen
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   real(real64) :: a(3,3), b(3), x(3), symmetric(2,2)
   real(real64), allocatable :: lu(:,:), values(:), vectors(:,:)
   integer(int32), allocatable :: pivots(:)
   integer :: i

   a = reshape([3._real64, 1._real64, 0._real64, &
                1._real64, 4._real64, 1._real64, &
                0._real64, 1._real64, 2._real64], [3,3])
   b = matmul(a, [1._real64, 2._real64, 3._real64])
   call lu_factor(a, ipvt=pivots, lu=lu)
   x = solve_lu(lu, pivots, b)
   if (.not. all(ieee_is_finite(x))) error stop 'Nonfinite solution'
   if (maxval(abs(x-[1._real64, 2._real64, 3._real64])) > 1.e-12_real64) error stop 'Incorrect solution'
   if (maxval(abs(matmul(a,x)-b)) > 1.e-12_real64) error stop 'Linear-system residual'
   print '(a,3f12.6)', 'Solution:', x

   symmetric = reshape([2._real64, 1._real64, 1._real64, 2._real64], [2,2])
   call eigen(symmetric, values, vectors)
   if (.not. all(ieee_is_finite(values))) error stop 'Nonfinite eigenvalues'
   if (maxval(abs(values-[1._real64, 3._real64])) > 1.e-12_real64) error stop 'Incorrect eigenvalues'
   if (.not. all(ieee_is_finite(vectors))) error stop 'Nonfinite eigenvectors'
   do i = 1, 2
      if (maxval(abs(matmul(symmetric,vectors(:,i))-values(i)*vectors(:,i))) > 1.e-12_real64) &
         error stop 'Eigenvector residual'
   end do
   print '(a,2f12.6)', 'Eigenvalues:', values
   print *, 'PASS linalg'
end program demo_linalg
