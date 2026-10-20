! Example: Arrays: reductions and locations
! Adapted from https://github.com/Beliavsky/FortranTip/blob/main/array_intrinsics.f90
! Try adding a second 9; which position does maxloc return?
program array_reductions
   implicit none
   integer, parameter :: v(3) = [4,1,9]
   print '(a,2(i0,1x))', 'Minimum and maximum: ', minval(v), maxval(v)
   print '(a,2(i0,1x))', 'Sum and product: ', sum(v), product(v)
   print '(a,2(i0,1x))', 'Positions of minimum and maximum: ', minloc(v), maxloc(v)
   print '(a,2(i0,1x))', 'Positions of 9 and missing 8: ', findloc(v,9), findloc(v,8)
end program array_reductions
