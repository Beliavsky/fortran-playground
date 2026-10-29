program demo_matrix_products
   use kinds, only: rk
   use formatmul, only: matmul
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   character(2), parameter :: methods(*) = ['m1', 'm2', 'm3', 'm4']
   real(rk) :: a(2, 3), b(3, 2), expected(2, 2), c(2, 2), vector(3), product(2)
   integer :: i, j, k, method

   a = reshape([1.0_rk, 4.0_rk, 2.0_rk, 5.0_rk, 3.0_rk, 6.0_rk], shape(a))
   b = reshape([7.0_rk, 9.0_rk, 11.0_rk, 8.0_rk, 10.0_rk, 12.0_rk], shape(b))
   ! An independent scalar-loop reference, rather than this module's MATMUL.
   expected = 0.0_rk
   do j = 1, 2
      do i = 1, 2
         do k = 1, 3
            expected(i, j) = expected(i, j) + a(i, k)*b(k, j)
         end do
      end do
   end do
   vector = [1.0_rk, -2.0_rk, 3.0_rk]
   ! At this pinned version, pass BOTH transpose flags when specifying either.
   ! A single explicitly false flag incorrectly selects a transposed branch.
   do method = 1, size(methods)
      c = matmul(a, b, option=methods(method))
      call check(c)
      c = matmul(a, b, transA=.false., transB=.false., option=methods(method))
      call check(c)
      c = matmul(transpose(a), b, transA=.true., transB=.false., option=methods(method))
      call check(c)
      c = matmul(a, transpose(b), transA=.false., transB=.true., option=methods(method))
      call check(c)
      c = matmul(transpose(a), transpose(b), transA=.true., transB=.true., option=methods(method))
      call check(c)
      product = matmul(a, vector, option=methods(method))
      if (any(.not. ieee_is_finite(product))) error stop 'nonfinite vector product'
      if (maxval(abs(product - [6.0_rk, 12.0_rk])) > 1.e-10_rk) error stop 'matrix-vector product'
      print '(a)', methods(method)//': rectangular, transposed and matrix-vector products checked'
   end do
   print '(a)', 'A times B:'
   do i = 1, 2
      print '(2f12.3)', expected(i, :)
   end do
   print '(a)', 'PASS formatmul'
contains
   subroutine check(matrix)
      real(rk), intent(in) :: matrix(:, :)
      if (any(.not. ieee_is_finite(matrix))) error stop 'nonfinite matrix product'
      if (maxval(abs(matrix - expected)) > 1.e-10_rk) error stop 'matrix product'
   end subroutine check
end program demo_matrix_products
