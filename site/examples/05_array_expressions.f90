! Example: Arrays: whole-array expressions
! Try changing the formula in both implementations.
program array_expressions
   implicit none
   integer :: i
   integer :: x(4) = [1,2,3,4], array_result(4), loop_result(4)
   array_result = x*x + 2*x + 1
   do i = 1, size(x)
      loop_result(i) = x(i)*x(i) + 2*x(i) + 1
   end do
   print '(a,*(i0,1x))', 'Array expression: ', array_result
   print '(a,*(i0,1x))', 'Loop: ', loop_result
   print '(a,l1)', 'Results agree: ', all(array_result == loop_result)
end program array_expressions
