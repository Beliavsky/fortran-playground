program demo_magic_squares
   use M_LA, only: mat_magic
   implicit none
   double precision, allocatable :: square(:, :)
   integer :: n, i, k, target, diagonal, reverse_diagonal

   print '(a)', 'Magic squares: order and common row/column/diagonal sum'
   do n = 3, 6
      allocate(square(n, n))
      call mat_magic(square, n, n)
      target = n*(n*n + 1)/2
      do i = 1, n
         if (nint(sum(square(i, :))) /= target) error stop 'row sum'
         if (nint(sum(square(:, i))) /= target) error stop 'column sum'
      end do
      diagonal = 0
      reverse_diagonal = 0
      do i = 1, n
         diagonal = diagonal + nint(square(i, i))
         reverse_diagonal = reverse_diagonal + nint(square(i, n + 1 - i))
      end do
      if (diagonal /= target .or. reverse_diagonal /= target) error stop 'diagonal sum'
      do k = 1, n*n
         if (count(nint(square) == k) /= 1) error stop 'entries must be a permutation of 1..n*n'
      end do
      print '(i3, i8)', n, target
      deallocate(square)
   end do
   print '(a)', 'PASS m_la'
end program demo_magic_squares
