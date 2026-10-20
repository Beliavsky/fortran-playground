! Example: Basics: loops and decisions
! Try changing n or summing only odd integers instead.
program sum_of_squares
   implicit none
   integer, parameter :: n = 10
   integer :: i, total, even_total
   total = 0
   even_total = 0
   do i = 1, n
      total = total + i*i
      if (mod(i,2) == 0) even_total = even_total + i*i
   end do
   print '(a,i0)', 'Sum of squares: ', total
   print '(a,i0)', 'Even squares: ', even_total
end program sum_of_squares
