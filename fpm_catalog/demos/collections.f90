program main
   use collections, only: list
   implicit none
   type(list) :: values
   class(*), pointer :: item
   integer :: i, total
   do i=1,4
      call values%push(10*i)
   end do
   call values%insert(2,5)
   if (values%count() /= 5) error stop 'incorrect list size'
   total = 0
   do i=1,values%count()
      item => values%get(i)
      select type(item)
      type is(integer)
         total = total+item
      class default
         error stop 'unexpected item type'
      end select
   end do
   if (total /= 105) error stop 'incorrect list contents'
   print *, 'List length and sum:', values%count(), total
   print *, 'PASS collections'
end program main
