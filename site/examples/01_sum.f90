! Example: Sum of squares
program main
   implicit none
   integer :: i, total
   total = 0
   do i = 1, 10
      total = total + i*i
   end do
   print *, total
end program main
