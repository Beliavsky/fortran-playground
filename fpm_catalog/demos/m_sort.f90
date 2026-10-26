program main
   use M_sort, only: sort_shell
   implicit none
   integer :: values(5)
   values = [5,2,4,1,3]
   call sort_shell(values, 'a')
   if (any(values /= [1,2,3,4,5])) error stop 'incorrect sort'
   print *, 'Sorted values:', values
   print *, 'PASS m_sort'
end program main
