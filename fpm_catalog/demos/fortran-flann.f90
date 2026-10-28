program nearest_neighbors
   use iso_c_binding, only: c_float, c_int
   use flann, only: flann_index, KDTreeSingleIndexParams, search_params
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer, parameter :: n=25, nq=3
   real(c_float), target :: points(2,n)
   real(c_float) :: queries(2,nq), distances(1,nq), direct(n)
   integer(c_int) :: indices(1,nq), status
   type(flann_index) :: tree
   integer :: i,j,k,expected
   k=0
   do j=0,4
      do i=0,4
         k=k+1
         points(:,k) = real([i,j],c_float)
      end do
   end do
   queries = reshape([0.1_c_float,0.2_c_float,2.8_c_float,1.1_c_float,3.9_c_float,3.8_c_float],[2,nq])
   tree = flann_index(points,KDTreeSingleIndexParams(),'Euclidean')
   call tree%build_index()
   indices = -1
   distances = -1
   call tree%knn_search(queries,indices,distances,1_c_int,search_params(checks=-1),stat=status)
   if (status/=0) error stop 'Nearest-neighbor search failed'
   if (.not. all(ieee_is_finite(distances))) error stop 'Nonfinite distance'
   print '(a)', ' Query point        Nearest point       Squared distance'
   do j=1,nq
      direct = [(sum((points(:,i)-queries(:,j))**2),i=1,n)]
      expected = minloc(direct,dim=1)
      ! FLANN returns C-style indices, starting at zero.
      if (indices(1,j)+1/=expected) error stop 'Neighbor index check'
      if (abs(distances(1,j)-direct(expected))>1.e-5_c_float) error stop 'Distance check'
      print '(2f7.2,4x,2f7.2,4x,f12.6)', queries(:,j),points(:,expected),distances(1,j)
   end do
   print *, 'PASS fortran-flann'
end program
