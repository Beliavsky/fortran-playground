! Example: Arrays: construction and slicing
! Try changing the stride in a(1:6:2) from 2 to 3.
program array_slices
   implicit none
   integer :: i
   integer :: a(6)
   a = [(i*i, i=1,6)]
   print '(a,*(i0,1x))', 'Squares: ', a
   print '(a,*(i0,1x))', 'Every other element: ', a(1:6:2)
   print '(a,*(i0,1x))', 'Reversed: ', a(6:1:-1)
end program array_slices
