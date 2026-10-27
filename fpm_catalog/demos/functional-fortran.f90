program main
   use functional, only: arange, reverse, set
   implicit none
   integer, allocatable :: values(:)
   values = arange(1, 9, 2)
   if (any(values /= [1,3,5,7,9])) error stop 'incorrect range'
   if (any(reverse(values) /= [9,7,5,3,1])) error stop 'incorrect reversal'
   if (size(set([2,1,2,3,1])) /= 3) error stop 'incorrect unique values'
   print *, 'Odd numbers:', values
   print *, 'Reversed:', reverse(values)
   print *, 'PASS functional-fortran'
end program
