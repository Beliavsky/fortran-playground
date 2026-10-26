program main
   use M_orderpack, only: rank
   implicit none
   real :: values(4)
   integer :: indices(4)
   values = [30.0,10.0,40.0,20.0]
   call rank(values,indices)
   if (any(indices /= [2,4,1,3])) error stop 'incorrect ranks'
   print *, 'Indices in ascending order:', indices
   print *, 'Ordered values:', values(indices)
   print *, 'PASS orderpack'
end program main
