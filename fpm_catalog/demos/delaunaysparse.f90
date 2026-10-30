program main
   use delsparse_mod, only: R8, delaunaysparses
   implicit none
   real(R8) :: points(2,9), queries(2,3), original(2,3), data(1,9), result(1,3), weights(3,3)
   real(R8) :: expected(3), tolerance
   integer :: simplices(3,3), status(3), i, j, k
   ! An irregular grid avoids square-grid diagonal ties; queries are strictly interior.
   points = reshape([0.0_R8,0.0_R8, 1.0_R8,0.0_R8, 0.0_R8,1.0_R8, &
      1.0_R8,1.0_R8, 0.21_R8,0.31_R8, 0.72_R8,0.24_R8, &
      0.32_R8,0.78_R8, 0.76_R8,0.69_R8, 0.51_R8,0.48_R8],[2,9])
   queries = reshape([0.3_R8,0.4_R8, 0.6_R8,0.5_R8, 0.7_R8,0.7_R8],[2,3])
   original = queries
   data(1,:) = 2*points(1,:)-3*points(2,:)+1
   expected = 2*queries(1,:)-3*queries(2,:)+1
   call delaunaysparses(2,9,points,3,queries,simplices,weights,status,interp_in=data,interp_out=result)
   tolerance = 1.0e-10_R8
   if (any(status /= 0)) error stop 'interpolation status'
   if (maxval(abs(result(1,:)-expected)) > tolerance) error stop 'linear reproduction'
   do i = 1, 3
      if (abs(sum(weights(:,i))-1) > tolerance) error stop 'barycentric sum'
      if (any(weights(:,i) < -tolerance)) error stop 'barycentric sign'
      do j = 1, 3
         k = simplices(j,i)
         if (k < 1 .or. k > 9) error stop 'vertex index'
      end do
      print '(a,2f7.3,a,f10.6)', 'At ',original(:,i),' interpolated value: ',result(1,i)
   end do
   print '(a,es12.3)', 'Maximum error for 2*x-3*y+1: ', maxval(abs(result(1,:)-expected))
   print '(a)', 'PASS delaunaysparse'
end program main
