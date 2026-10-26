program main
   use linked_list_module, only: list
   implicit none
   type(list) :: values
   class(*), pointer :: item
   values = list(.false.)
   call values%add_clone('answer',42)
   call values%get('answer',item)
   if (.not. associated(item)) error stop 'missing value'
   select type(item)
   type is(integer)
      if (item /= 42) error stop 'incorrect value'
      print *, 'Stored answer:', item
   class default
      error stop 'incorrect type'
   end select
   call values%destroy()
   print *, 'PASS flist'
end program main
