program main
   use M_list, only: locate, insert
   implicit none
   integer, allocatable :: values(:)
   integer :: place
   ! M_list keeps arrays in descending order.
   values = [30,10]
   call locate(values, 20, place)
   if (place >= 1) error stop 'unexpected existing entry'
   call insert(values, 20, abs(place))
   if (any(values /= [30,20,10])) error stop 'incorrect insertion'
   call locate(values, 20, place)
   if (place /= 2) error stop 'incorrect lookup'
   print *, 'Sorted values:', values
   print *, 'PASS m_list'
end program
