program main
   use sorting_module, only: sort_ascending, binary_search
   implicit none
   integer :: values(5), position
   values = [9,3,7,1,5]
   call sort_ascending(values)
   if (any(values /= [1,3,5,7,9])) error stop 'sort failed'
   position = binary_search(7, values)
   if (position /= 4) error stop 'search failed'
   print *, 'Sorted values:', values
   print *, 'Position of 7:', position
   print *, 'PASS fortran-search-and-sort'
end program main
