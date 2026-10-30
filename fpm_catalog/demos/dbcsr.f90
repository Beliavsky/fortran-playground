! Serial block-sparse multiplication, following the author's matrix examples.
program main
   use dbcsr_api
   use, intrinsic :: iso_fortran_env, only: real64
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   type(dbcsr_type) :: a, b, c
   type(dbcsr_distribution_type) :: distribution
   integer, pointer :: row_sizes(:), col_sizes(:), rows(:), columns(:)
   real(real64), pointer :: block(:,:)
   real(real64) :: dense_a(4,4), dense_b(4,4), result(4,4), expected(4,4), residual
   integer :: i, j, r, s
   logical :: transposed, found
   allocate(row_sizes(2), col_sizes(2), rows(2), columns(2))
   row_sizes = 2
   col_sizes = 2
   rows = 0
   columns = 0
   call dbcsr_init_lib(0)
   call dbcsr_distribution_new(distribution, group=0, row_dist=rows, col_dist=columns)
   call dbcsr_create(a, 'A', distribution, dbcsr_type_no_symmetry, row_sizes, col_sizes, &
      data_type=dbcsr_type_real_8)
   call dbcsr_create(b, 'B', distribution, dbcsr_type_no_symmetry, row_sizes, col_sizes, &
      data_type=dbcsr_type_real_8)
   call dbcsr_create(c, 'C', distribution, dbcsr_type_no_symmetry, row_sizes, col_sizes, &
      data_type=dbcsr_type_real_8)
   dense_a = 0.0_real64
   dense_a(1:2,1:2) = reshape([2.0_real64,0.0_real64,1.0_real64,3.0_real64],[2,2])
   dense_a(3:4,3:4) = reshape([4.0_real64,1.0_real64,0.0_real64,5.0_real64],[2,2])
   dense_b = 0.0_real64
   dense_b(1:2,1:2) = reshape([1.0_real64,0.0_real64,0.0_real64,2.0_real64],[2,2])
   dense_b(1:2,3:4) = reshape([1.0_real64,2.0_real64,0.0_real64,1.0_real64],[2,2])
   dense_b(3:4,3:4) = reshape([3.0_real64,0.0_real64,0.0_real64,4.0_real64],[2,2])
   do j=1,2
      do i=1,2
         r=2*i-1
         s=2*j-1
         if (any(dense_a(r:r+1,s:s+1) /= 0.0_real64)) &
            call dbcsr_put_block(a, i, j, dense_a(r:r+1,s:s+1))
         if (any(dense_b(r:r+1,s:s+1) /= 0.0_real64)) &
            call dbcsr_put_block(b, i, j, dense_b(r:r+1,s:s+1))
      end do
   end do
   call dbcsr_finalize(a)
   call dbcsr_finalize(b)
   call dbcsr_finalize(c)
   call dbcsr_multiply('N', 'N', 1.0_real64, a, b, 0.0_real64, c)
   result = 0.0_real64
   do j=1,2
      do i=1,2
         call dbcsr_get_block_p(c, i, j, block, transposed, found)
         if (.not. found) cycle
         r=2*i-1
         s=2*j-1
         if (transposed) then
            result(r:r+1,s:s+1) = transpose(block)
         else
            result(r:r+1,s:s+1) = block
         end if
      end do
   end do
   expected = matmul(dense_a,dense_b)
   residual = maxval(abs(result-expected))
   if (.not. all(ieee_is_finite(result)) .or. residual > 1.0e-12_real64) &
      error stop 'Block-sparse product differs from MATMUL'
   call dbcsr_release(a)
   call dbcsr_release(b)
   call dbcsr_release(c)
   call dbcsr_distribution_release(distribution)
   call dbcsr_finalize_lib()
   deallocate(row_sizes, col_sizes, rows, columns)
   print '(a)', 'Block-sparse matrix product:'
   do i=1,4
      print '(4f9.2)', result(i,:)
   end do
   print '(a,es12.4)', 'Maximum difference from MATMUL: ', residual
   print '(a)', 'PASS dbcsr'
end program main
