program main
   use string_sort_module, only: lexical_sort_natural_recursive
   implicit none
   character(8) :: names(3)
   names = [character(8) :: 'file10','file2','file1']
   call lexical_sort_natural_recursive(names, case_sensitive=.true.)
   if (any(names /= [character(8) :: 'file1','file2','file10'])) error stop 'sort failed'
   print *, names
   print *, 'PASS stringsort'
end program main
