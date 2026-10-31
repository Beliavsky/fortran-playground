! Independent API consumer; MIT: licenses/spatial-nufft-drivers-MIT.txt.
program affine_reference
   use delsparse_mod, only: R8, delaunaysparses
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer, parameter :: n = 10, m = 6
   real(R8), parameter :: tol = 1.e-10_R8
   real(R8) :: points(3,n),original(3,n),queries(3,m),saved_queries(3,m),data(3,n),result(3,m)
   real(R8) :: weights(4,m),coeff(4),reconstructed(3),expected(3),a(3),b(3),c(3),volume
   integer :: simplices(4,m),status(m),i,j,k,l
   points(:,1) = [0._R8,0._R8,0._R8]
   points(:,2) = [2._R8,0._R8,0._R8]
   points(:,3) = [.2_R8,1.5_R8,0._R8]
   points(:,4) = [.1_R8,.3_R8,1.7_R8]
   do i = 5,n
      coeff = [real(i-3,R8),real(mod(i,3)+1,R8),real(mod(i+1,4)+1,R8),3._R8]
      coeff = coeff/sum(coeff)
      points(:,i) = matmul(points(:,:4),coeff)
   end do
   do i = 1,m
      coeff = [real(2*i+1,R8),real(i+4,R8),real(2*i+3,R8),real(3*i+2,R8)]
      coeff = coeff/sum(coeff)
      queries(:,i) = matmul(points(:,:4),coeff)
   end do
   original = points
   saved_queries = queries
   do i = 1,n
      data(:,i) = fields(points(:,i))
   end do
   ! This routine rescales its coordinates in place; references use preserved originals.
   call delaunaysparses(3,n,points,m,queries,simplices,weights,status,interp_in=data,interp_out=result)
   if (any(status /= 0)) error stop 'scattered interpolation status'
   if (.not. all(ieee_is_finite(weights))) error stop 'nonfinite barycentric weights'
   if (.not. all(ieee_is_finite(result))) error stop 'nonfinite interpolated values'
   do i = 1,m
      if (abs(sum(weights(:,i))-1._R8) > tol) error stop 'partition of unity'
      if (minval(weights(:,i)) < -tol) error stop 'outside returned simplex'
      reconstructed = 0._R8
      expected = 0._R8
      do j = 1,4
         k = simplices(j,i)
         if (k < 1 .or. k > n) error stop 'simplex index range'
         do l = 1,j-1
            if (simplices(l,i) == k) error stop 'duplicate simplex vertex'
         end do
         reconstructed = reconstructed+weights(j,i)*original(:,k)
         expected = expected+weights(j,i)*fields(original(:,k))
      end do
      a = original(:,simplices(2,i))-original(:,simplices(1,i))
      b = original(:,simplices(3,i))-original(:,simplices(1,i))
      c = original(:,simplices(4,i))-original(:,simplices(1,i))
      volume = a(1)*(b(2)*c(3)-b(3)*c(2))-a(2)*(b(1)*c(3)-b(3)*c(1)) &
         +a(3)*(b(1)*c(2)-b(2)*c(1))
      if (abs(volume) < tol) error stop 'degenerate returned tetrahedron'
      if (maxval(abs(reconstructed-saved_queries(:,i))) > tol) error stop 'barycentric query reconstruction'
      if (maxval(abs(result(:,i)-expected)) > tol) error stop 'scalar weighted field reference'
      expected = fields(saved_queries(:,i))
      if (maxval(abs(result(:2,i)-expected(:2))) > tol) error stop 'exact constant and affine reproduction'
      print '(a,i0,a,f10.6,a,f10.6)', 'Query ',i,': affine=',result(2,i), &
         ' piecewise linear squared radius=',result(3,i)
   end do
   print '(a)', 'Six 3D queries checked: affine reproduction, simplex geometry, and three-channel weighted interpolation.'
   print '(a)', 'PASS delaunay-affine-reference'
contains
   function fields(x) result(y)
      real(R8), intent(in) :: x(3)
      real(R8) :: y(3)
      y = [1._R8,2*x(1)-3*x(2)+.5_R8*x(3)+1._R8,sum(x*x)]
   end function fields
end program affine_reference
