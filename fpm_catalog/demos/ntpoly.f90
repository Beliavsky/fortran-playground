! One MPI process. A = [5 4; 4 5] has eigenvalues 1 and 9.
program main
   use mpi, only: MPI_Init_thread, MPI_THREAD_SERIALIZED, MPI_Finalize, MPI_Comm_size, MPI_COMM_WORLD, MPI_SUCCESS
   use DataTypesModule, only: NTREAL
   use ProcessGridModule, only: ConstructProcessGrid, DestructProcessGrid
   use PSMatrixModule, only: Matrix_ps, ConstructEmptyMatrix, FillMatrixFromTripletList, &
      GatherMatrixTripletList, DestructMatrix
   use TripletModule, only: Triplet_r
   use TripletListModule, only: TripletList_r, ConstructTripletList, AppendToTripletList, DestructTripletList
   use SolverParametersModule, only: SolverParameters_t, ConstructSolverParameters, DestructSolverParameters
   use SquareRootSolversModule, only: SquareRoot, InverseSquareRoot
   use InverseSolversModule, only: Invert
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
   type(Matrix_ps) :: matrix, root, inverse_root, inverse
   type(TripletList_r) :: entries
   type(Triplet_r) :: entry
   type(SolverParameters_t) :: parameters
   real(NTREAL) :: a(2,2), result(2,2), expected(2,2), identity(2,2), residual
   integer :: ierr, processes, provided, i, j
   call MPI_Init_thread(MPI_THREAD_SERIALIZED, provided, ierr)
   if (ierr /= MPI_SUCCESS) error stop 'MPI initialization failed'
   if (provided < MPI_THREAD_SERIALIZED) error stop 'MPI thread support is insufficient'
   call MPI_Comm_size(MPI_COMM_WORLD, processes, ierr)
   if (ierr /= MPI_SUCCESS .or. processes /= 1) error stop 'This example uses one MPI process'
   call ConstructProcessGrid(MPI_COMM_WORLD, 1, 1, 1)
   a = reshape([5.0_NTREAL,4.0_NTREAL,4.0_NTREAL,5.0_NTREAL], [2,2])
   identity = reshape([1.0_NTREAL,0.0_NTREAL,0.0_NTREAL,1.0_NTREAL], [2,2])
   call ConstructTripletList(entries)
   do j = 1, 2
      do i = 1, 2
         entry%index_row = i
         entry%index_column = j
         entry%point_value = a(i,j)
         call AppendToTripletList(entries, entry)
      end do
   end do
   call ConstructEmptyMatrix(matrix, 2)
   call FillMatrixFromTripletList(matrix, entries)
   call DestructTripletList(entries)
   call ConstructSolverParameters(parameters, converge_diff_in=1.0e-12_NTREAL, &
      threshold_in=1.0e-14_NTREAL, max_iterations_in=200, be_verbose_in=.false.)
   call SquareRoot(matrix, root, parameters)
   call extract(root, result)
   expected = reshape([2.0_NTREAL,1.0_NTREAL,1.0_NTREAL,2.0_NTREAL], [2,2])
   residual = maxval(abs(matmul(result,result)-a))
   if (maxval(abs(result-expected)) > 1.0e-9_NTREAL .or. residual > 1.0e-9_NTREAL) &
      error stop 'Matrix square root failed'
   print '(a)', 'Matrix square root:'
   do i = 1, 2
      print '(2f14.9)', result(i,:)
   end do
   print '(a,es12.4)', 'Square-root residual: ', residual
   call InverseSquareRoot(matrix, inverse_root, parameters)
   call extract(inverse_root, result)
   expected = reshape([2.0_NTREAL,-1.0_NTREAL,-1.0_NTREAL,2.0_NTREAL], [2,2])/3.0_NTREAL
   residual = maxval(abs(matmul(result,matmul(a,result))-identity))
   if (maxval(abs(result-expected)) > 1.0e-9_NTREAL .or. residual > 1.0e-9_NTREAL) &
      error stop 'Inverse square root failed'
   print '(a,es12.4)', 'Inverse-square-root residual: ', residual
   call Invert(matrix, inverse, parameters)
   call extract(inverse, result)
   expected = reshape([5.0_NTREAL,-4.0_NTREAL,-4.0_NTREAL,5.0_NTREAL], [2,2])/9.0_NTREAL
   residual = maxval(abs(matmul(a,result)-identity))
   if (maxval(abs(result-expected)) > 1.0e-9_NTREAL .or. residual > 1.0e-9_NTREAL) &
      error stop 'Matrix inverse failed'
   print '(a,es12.4)', 'Matrix-inverse residual: ', residual
   call DestructMatrix(inverse)
   call DestructMatrix(inverse_root)
   call DestructMatrix(root)
   call DestructMatrix(matrix)
   call DestructSolverParameters(parameters)
   call DestructProcessGrid()
   call MPI_Finalize(ierr)
   if (ierr /= MPI_SUCCESS) error stop 'MPI finalization failed'
   print '(a)', 'PASS ntpoly'
contains
   subroutine extract(source, dense)
      type(Matrix_ps), intent(in) :: source
      real(NTREAL), intent(out) :: dense(2,2)
      type(TripletList_r) :: list
      integer :: k, row, column
      call GatherMatrixTripletList(source, list)
      dense = 0.0_NTREAL
      do k = 1, list%CurrentSize
         row = list%data(k)%index_row
         column = list%data(k)%index_column
         if (min(row,column) < 1 .or. max(row,column) > 2) error stop 'Matrix index out of range'
         dense(row,column) = dense(row,column) + list%data(k)%point_value
      end do
      call DestructTripletList(list)
      if (.not. all(ieee_is_finite(dense))) error stop 'Nonfinite matrix entries'
   end subroutine extract
end program main
