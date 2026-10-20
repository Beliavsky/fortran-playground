! Example: Arrays: matrices and column-major order
! Try changing b; reshape fills columns first, not rows.
program matrices
   implicit none
   integer :: a(2,2), b(2,2), c(2,2), at(2,2), i
   a = reshape([1,2,3,4], [2,2])
   b = reshape([2,0,0,2], [2,2])
   c = matmul(a,b)
   at = transpose(a)
   do i = 1, 2
      print '(a,i0,a,2(i0,1x))', 'A row ', i, ': ', a(i,:)
   end do
   do i = 1, 2
      print '(a,i0,a,2(i0,1x))', 'Transpose row ', i, ': ', at(i,:)
   end do
   do i = 1, 2
      print '(a,i0,a,2(i0,1x))', 'Product row ', i, ': ', c(i,:)
   end do
end program matrices
