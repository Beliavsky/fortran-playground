! Example: Memory: allocatable arrays
! Try adding more values to the second assignment.
program allocatable_arrays
   implicit none
   integer, allocatable :: v(:)
   print '(a,l1)', 'Initially allocated: ', allocated(v)
   v = [4,9] ! Assignment allocates the array automatically.
   print '(a,i0)', 'First size: ', size(v)
   v = [v,16,25] ! A different shape causes automatic reallocation.
   print '(a,i0)', 'New size: ', size(v)
   print '(a,*(i0,1x))', 'Values: ', v
   deallocate(v)
   print '(a,l1)', 'Allocated after deallocate: ', allocated(v)
end program allocatable_arrays
