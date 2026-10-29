program main
   use array_range, only: array2d_range_type, to_array2d_range
   implicit none
   type(array2d_range_type) :: bounds
   integer :: values(-1:1, 4:5), i, j, total, visited
   bounds = to_array2d_range([lbound(values), ubound(values)])
   if (any(bounds%to_array() /= [-1,4,1,5])) error stop 'bounds round trip'
   total = 0
   visited = 0
   do j = bounds%rank(2)%lower, bounds%rank(2)%upper
      do i = bounds%rank(1)%lower, bounds%rank(1)%upper
         values(i,j) = i+10*j
         total = total+values(i,j)
         visited = visited+1
      end do
   end do
   if (visited /= 6 .or. total /= 270) error stop 'array traversal'
   print *, 'Bounds:', bounds%to_array()
   print *, 'Visited:', visited, ' sum:', total
   print *, 'PASS array_range'
end program
