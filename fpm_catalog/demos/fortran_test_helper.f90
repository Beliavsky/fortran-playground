program main
   use fortran_test_helper, only: assert
   implicit none
   real :: x(3)
   x = [1.0,2.0,3.0]
   if (.not. assert(x*x, [1.0,4.0,9.0], 1.e-6)) error stop 'array assertion failed'
   if (assert(1.0, 2.0, 1.e-6)) error stop 'unequal values accepted'
   print *, 'Checked array arithmetic and unequal scalars.'
   print *, 'PASS fortran_test_helper'
end program
