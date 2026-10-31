! Independent API consumer; MIT: licenses/matrix-roots-box-drivers-MIT.txt.
program matrix_root_reference
   use mpi, only: MPI_Init_thread,MPI_THREAD_SERIALIZED,MPI_Finalize,MPI_Comm_size,MPI_COMM_WORLD,MPI_SUCCESS
   use DataTypesModule, only: NTREAL
   use ProcessGridModule, only: ConstructProcessGrid,DestructProcessGrid
   use PSMatrixModule, only: Matrix_ps,ConstructEmptyMatrix,FillMatrixFromTripletList, &
      GatherMatrixTripletList,DestructMatrix
   use TripletModule, only: Triplet_r
   use TripletListModule, only: TripletList_r,ConstructTripletList,AppendToTripletList,DestructTripletList
   use SolverParametersModule, only: SolverParameters_t,ConstructSolverParameters,DestructSolverParameters
   use SquareRootSolversModule, only: SquareRoot,InverseSquareRoot
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   real(NTREAL), parameter :: root_pairs(2,4) = reshape([1._NTREAL,2._NTREAL,1._NTREAL,3._NTREAL, &
      .5_NTREAL,2._NTREAL,2._NTREAL,4._NTREAL],[2,4])
   type(Matrix_ps) :: matrix,root_matrix,inverse_matrix
   type(TripletList_r) :: entries
   type(Triplet_r) :: entry
   type(SolverParameters_t) :: parameters
   real(NTREAL), allocatable :: a(:,:),q(:,:),r(:),root(:,:),inverse_root(:,:),expected(:,:),expected_inverse(:,:)
   real(NTREAL) :: c,s,left,right,product,value,identity,max_error,max_residual,error
   integer :: ierr,provided,processes,n,pair,rotation,i,j,k,l,cases
   call MPI_Init_thread(MPI_THREAD_SERIALIZED,provided,ierr)
   if (ierr /= MPI_SUCCESS .or. provided < MPI_THREAD_SERIALIZED) error stop 'MPI initialization/thread support'
   call MPI_Comm_size(MPI_COMM_WORLD,processes,ierr)
   if (ierr /= MPI_SUCCESS .or. processes /= 1) error stop 'one MPI process required'
   call ConstructProcessGrid(MPI_COMM_WORLD,1,1,1)
   cases = 0
   max_error = 0._NTREAL
   max_residual = 0._NTREAL
   do n = 2,3
      allocate(a(n,n),q(n,n),r(n),root(n,n),inverse_root(n,n),expected(n,n),expected_inverse(n,n))
      do pair = 1,4
         r(:2) = root_pairs(:,pair)
         if (n == 3) r(3) = sum(r(:2))/2
         do rotation = 1,3
            select case(rotation)
            case(1)
               c = 1._NTREAL
               s = 0._NTREAL
            case(2)
               c = .6_NTREAL
               s = .8_NTREAL
            case(3)
               c = sqrt(.5_NTREAL)
               s = c
            end select
            q = 0._NTREAL
            q(1,1) = c
            q(1,2) = -s
            q(2,1) = s
            q(2,2) = c
            if (n == 3) q(3,3) = 1._NTREAL
            a = 0._NTREAL
            expected = 0._NTREAL
            expected_inverse = 0._NTREAL
            do j = 1,n
               do i = 1,n
                  do k = 1,n
                     a(i,j) = a(i,j)+q(i,k)*r(k)**2*q(j,k)
                     expected(i,j) = expected(i,j)+q(i,k)*r(k)*q(j,k)
                     expected_inverse(i,j) = expected_inverse(i,j)+q(i,k)/r(k)*q(j,k)
                  end do
               end do
            end do
            call ConstructTripletList(entries)
            do j = 1,n
               do i = 1,n
                  if (a(i,j) == 0) cycle
                  entry%index_row = i
                  entry%index_column = j
                  entry%point_value = a(i,j)
                  call AppendToTripletList(entries,entry)
               end do
            end do
            call ConstructEmptyMatrix(matrix,n)
            call FillMatrixFromTripletList(matrix,entries)
            call DestructTripletList(entries)
            call ConstructSolverParameters(parameters,converge_diff_in=1.e-12_NTREAL,threshold_in=1.e-14_NTREAL, &
               max_iterations_in=200,be_verbose_in=.false.)
            call SquareRoot(matrix,root_matrix,parameters)
            call extract(root_matrix,root)
            call InverseSquareRoot(matrix,inverse_matrix,parameters)
            call extract(inverse_matrix,inverse_root)
            error = max(maxval(abs(root-expected))/max(1._NTREAL,maxval(abs(expected))), &
               maxval(abs(inverse_root-expected_inverse))/max(1._NTREAL,maxval(abs(expected_inverse))))
            max_error = max(max_error,error)
            if (error > 2.e-8_NTREAL) error stop 'known principal matrix functions'
            if (maxval(abs(root-transpose(root))) > 2.e-9_NTREAL &
               .or. maxval(abs(inverse_root-transpose(inverse_root))) > 2.e-9_NTREAL) error stop 'matrix symmetry'
            do j = 1,n
               do i = 1,n
                  identity = 0._NTREAL
                  if (i == j) identity = 1._NTREAL
                  left = -a(i,j)
                  right = -identity
                  product = -identity
                  do k = 1,n
                     left = left+root(i,k)*root(k,j)
                     product = product+root(i,k)*inverse_root(k,j)
                     do l = 1,n
                        right = right+inverse_root(i,k)*a(k,l)*inverse_root(l,j)
                     end do
                  end do
                  value = max(abs(left)/max(1._NTREAL,maxval(abs(a))),abs(right),abs(product))
                  max_residual = max(max_residual,value)
                  if (value > 5.e-8_NTREAL) error stop 'independent matrix-function residual'
               end do
            end do
            print '(a,i0,a,i0,a,i0,a,es12.4)', 'Dimension=',n,' pair=',pair,' rotation=',rotation,' error=',error
            call DestructMatrix(inverse_matrix)
            call DestructMatrix(root_matrix)
            call DestructMatrix(matrix)
            call DestructSolverParameters(parameters)
            cases = cases+1
         end do
      end do
      deallocate(a,q,r,root,inverse_root,expected,expected_inverse)
   end do
   call DestructProcessGrid()
   call MPI_Finalize(ierr)
   if (ierr /= MPI_SUCCESS .or. cases /= 24) error stop 'MPI finalization/fixture count'
   print '(a)', '24 SPD fixtures, 48 matrix functions: known orthogonal factors and positive square-root eigenvalues.'
   print '(a,es12.4)', 'Maximum normalized closed-form error: ',max_error
   print '(a,es12.4)', 'Maximum independent product residual: ',max_residual
   print '(a)', 'PASS ntpoly-matrix-root-reference'
contains
   subroutine extract(source,dense)
      type(Matrix_ps), intent(in) :: source
      real(NTREAL), intent(out) :: dense(:,:)
      type(TripletList_r) :: list
      integer :: index,row,column
      call GatherMatrixTripletList(source,list)
      dense = 0._NTREAL
      do index = 1,list%CurrentSize
         row = list%data(index)%index_row
         column = list%data(index)%index_column
         if (min(row,column) < 1 .or. max(row,column) > size(dense,1)) error stop 'matrix triplet bounds'
         dense(row,column) = dense(row,column)+list%data(index)%point_value
      end do
      call DestructTripletList(list)
      if (.not. all(ieee_is_finite(dense))) error stop 'nonfinite matrix function'
   end subroutine extract
end program matrix_root_reference
