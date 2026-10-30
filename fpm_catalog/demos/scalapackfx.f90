! A one-process BLACS grid illustrates the API, not distributed performance.
program main
   use libscalapackfx_module
   use, intrinsic :: iso_fortran_env, only: dp => real64
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   type(blacsgrid) :: grid
   real(dp), allocatable :: a(:,:), vectors(:,:)
   real(dp) :: original(3,3), eigenvalues(3), expected(3), identity(3,3), residual, orthogonality
   integer :: desca(DLEN_), descz(DLEN_), rank, processes, info, i
   call blacsfx_pinfo(rank, processes)
   if (processes /= 1) error stop 'This example uses exactly one MPI process'
   call grid%initgrid(1, 1)
   call scalafx_creatematrix(grid, 3, 3, 2, 2, a, desca, info=info)
   if (info /= 0) error stop 'Matrix descriptor failed'
   call scalafx_creatematrix(grid, 3, 3, 2, 2, vectors, descz, info=info)
   if (info /= 0) error stop 'Eigenvector descriptor failed'
   original = reshape([2.0_dp,1.0_dp,0.0_dp, 1.0_dp,2.0_dp,1.0_dp, 0.0_dp,1.0_dp,2.0_dp], [3,3])
   a = original
   call scalafx_psyev(a, desca, eigenvalues, vectors, descz, jobz='V', uplo='L', info=info)
   if (info /= 0) error stop 'ScaLAPACK eigensolver failed'
   if (.not. all(ieee_is_finite(eigenvalues)) .or. .not. all(ieee_is_finite(vectors))) &
      error stop 'Nonfinite eigensystem'
   expected = [2.0_dp-sqrt(2.0_dp), 2.0_dp, 2.0_dp+sqrt(2.0_dp)]
   residual = 0.0_dp
   identity = 0.0_dp
   do i = 1, 3
      identity(i,i) = 1.0_dp
      residual = max(residual, maxval(abs(matmul(original,vectors(:,i))-eigenvalues(i)*vectors(:,i))))
   end do
   orthogonality = maxval(abs(matmul(transpose(vectors),vectors)-identity))
   if (maxval(abs(eigenvalues-expected)) > 1.0e-10_dp .or. residual > 1.0e-10_dp .or. &
       orthogonality > 1.0e-10_dp) error stop 'Eigensystem checks failed'
   print '(a,3f14.9)', 'Eigenvalues: ', eigenvalues
   print '(a,es12.4)', 'Maximum eigenpair residual: ', residual
   print '(a,es12.4)', 'Orthogonality residual: ', orthogonality
   call grid%destruct()
   call blacsfx_exit(keepmpi=.false.)
   print '(a)', 'PASS scalapackfx'
end program main
