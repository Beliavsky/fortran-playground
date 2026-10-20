! Example: Procedures: elemental functions
! Adapted from https://github.com/Beliavsky/FortranTip/blob/main/elemental.f90
! Try passing an array for length and a scalar for width.
program elemental_functions
   implicit none
   print '(a,i0)', 'Scalar arguments: ', area(3,4)
   print '(a,*(i0,1x))', 'Scalar and array: ', area(3,[4,5])
   print '(a,*(i0,1x))', 'Two arrays: ', area([3,4],[4,5])
contains
   elemental integer function area(length,width)
      integer, intent(in) :: length, width
      area = length*width
   end function area
end program elemental_functions
