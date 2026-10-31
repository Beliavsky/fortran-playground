! Independent API consumer; see licenses/gmres-inverse-drivers-MIT.txt.
program checked_ntpoly_inverse
   use mpi, only: MPI_Init_thread,MPI_THREAD_SERIALIZED,MPI_Finalize,MPI_Comm_size,MPI_COMM_WORLD,MPI_SUCCESS
   use DataTypesModule, only: NTREAL
   use ProcessGridModule, only: ConstructProcessGrid,DestructProcessGrid
   use PSMatrixModule, only: Matrix_ps,ConstructEmptyMatrix,FillMatrixFromTripletList, &
      GatherMatrixTripletList,DestructMatrix
   use TripletModule, only: Triplet_r
   use TripletListModule, only: TripletList_r,ConstructTripletList,AppendToTripletList,DestructTripletList
   use SolverParametersModule, only: SolverParameters_t,ConstructSolverParameters,DestructSolverParameters
   use InverseSolversModule, only: Invert
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer, parameter :: sizes(4)=[2,3,5,8]
   real(NTREAL), parameter :: conditions(3)=[2.0_NTREAL,10.0_NTREAL,50.0_NTREAL]
   integer :: ierr,provided,processes,s,condition,scale,rotation,cases=0,entries=0
   real(NTREAL) :: worst_error=0,worst_left=0,worst_right=0,worst_symmetry=0
   call MPI_Init_thread(MPI_THREAD_SERIALIZED,provided,ierr)
   if (ierr/=MPI_SUCCESS.or.provided<MPI_THREAD_SERIALIZED) error stop 'MPI initialization/thread support'
   call MPI_Comm_size(MPI_COMM_WORLD,processes,ierr)
   if (ierr/=MPI_SUCCESS.or.processes/=1) error stop 'one MPI process required'
   call ConstructProcessGrid(MPI_COMM_WORLD,1,1,1)
   do s=1,4
      do condition=1,3
         do scale=1,2
            do rotation=0,1
               call fixture(sizes(s),conditions(condition),scale,rotation)
            end do
         end do
      end do
   end do
   call DestructProcessGrid()
   call MPI_Finalize(ierr)
   if (ierr/=MPI_SUCCESS) error stop 'MPI finalization'
   print '(a,i0)', 'SPD matrix inversions: ',cases
   print '(a,i0)', 'Analytic inverse entries: ',entries
   print '(a,es12.4)', 'Maximum normalized inverse error: ',worst_error
   print '(a,es12.4)', 'Maximum left identity residual: ',worst_left
   print '(a,es12.4)', 'Maximum right identity residual: ',worst_right
   print '(a,es12.4)', 'Maximum normalized symmetry error: ',worst_symmetry
   print '(a)', 'PASS ntpoly-inverse-reference'
contains
   subroutine fixture(n,condition,scale,rotation)
      integer, intent(in) :: n,scale,rotation
      real(NTREAL), intent(in) :: condition
      type(Matrix_ps) :: matrix,inverse
      type(TripletList_r) :: list
      type(Triplet_r) :: entry
      type(SolverParameters_t) :: parameters
      real(NTREAL) :: q(n,n),a(n,n),expected(n,n),values(n),result(n,n),original(n,n)
      real(NTREAL) :: amplitude,angle,c,s,col1(n),col2(n),value,left,right,error,symmetry
      integer :: i,j,k
      q=0
      do i=1,n
         q(i,i)=1
      end do
      if (rotation==1) then
         do j=1,n-1
            angle=0.2_NTREAL+0.07_NTREAL*j; c=cos(angle); s=sin(angle)
            col1=q(:,j); col2=q(:,j+1)
            q(:,j)=c*col1-s*col2; q(:,j+1)=s*col1+c*col2
         end do
      end if
      amplitude=0.25_NTREAL
      if (scale==2) amplitude=4
      values=[(amplitude*(1+(condition-1)*real(i-1,NTREAL)/real(n-1,NTREAL)),i=1,n)]
      a=0; expected=0
      do j=1,n
         do i=1,n
            do k=1,n
               a(i,j)=a(i,j)+q(i,k)*values(k)*q(j,k)
               expected(i,j)=expected(i,j)+q(i,k)*q(j,k)/values(k)
            end do
         end do
      end do
      call ConstructTripletList(list)
      do j=1,n
         do i=1,n
            entry%index_row=i; entry%index_column=j; entry%point_value=a(i,j)
            call AppendToTripletList(list,entry)
         end do
      end do
      call ConstructEmptyMatrix(matrix,n)
      call FillMatrixFromTripletList(matrix,list)
      call DestructTripletList(list)
      call ConstructSolverParameters(parameters,converge_diff_in=1e-12_NTREAL,threshold_in=1e-14_NTREAL, &
         max_iterations_in=200,be_verbose_in=.false.)
      call Invert(matrix,inverse,parameters)
      call extract(inverse,result)
      call extract(matrix,original)
      if (maxval(abs(original-a))/maxval(abs(a))>2e-12_NTREAL) error stop 'input matrix changed'
      error=maxval(abs(result-expected)/(1+abs(expected)))
      symmetry=maxval(abs(result-transpose(result)))/(1+maxval(abs(expected)))
      left=0; right=0
      do j=1,n
         do i=1,n
            value=0
            do k=1,n
               value=value+a(i,k)*result(k,j)
            end do
            left=max(left,abs(value-real(merge(1,0,i==j),NTREAL)))
            value=0
            do k=1,n
               value=value+result(i,k)*a(k,j)
            end do
            right=max(right,abs(value-real(merge(1,0,i==j),NTREAL)))
         end do
      end do
      worst_error=max(worst_error,error); worst_left=max(worst_left,left); worst_right=max(worst_right,right)
      worst_symmetry=max(worst_symmetry,symmetry)
      if (error>5e-9_NTREAL.or.symmetry>5e-9_NTREAL.or.max(left,right)>5e-9_NTREAL) &
         error stop 'analytic inverse/two-sided product mismatch'
      call DestructMatrix(inverse); call DestructMatrix(matrix); call DestructSolverParameters(parameters)
      cases=cases+1; entries=entries+n*n
   end subroutine fixture
   subroutine extract(source,dense)
      type(Matrix_ps), intent(in) :: source
      real(NTREAL), intent(out) :: dense(:,:)
      type(TripletList_r) :: list
      integer :: k,i,j,n
      n=size(dense,1)
      call GatherMatrixTripletList(source,list)
      dense=0
      do k=1,list%CurrentSize
         i=list%data(k)%index_row; j=list%data(k)%index_column
         if (min(i,j)<1.or.max(i,j)>n) error stop 'gathered matrix index'
         dense(i,j)=dense(i,j)+list%data(k)%point_value
      end do
      call DestructTripletList(list)
      if (.not.all(ieee_is_finite(dense))) error stop 'nonfinite matrix entries'
   end subroutine extract
end program checked_ntpoly_inverse
