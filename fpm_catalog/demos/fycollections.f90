! Adapted from FyCollections integer/string list examples (BSD-2-Clause).
program typed_lists
   use type_intlist, only: IntList, IntList_init, int_size => size
   use type_stringlist, only: StringList, StringList_init, string_size => size
   implicit none
   type(IntList), allocatable :: numbers
   type(StringList), allocatable :: words
   integer :: i

   allocate(numbers, words)
   call IntList_init(numbers)
   call StringList_init(words)
   do i = 1, 3
      call numbers%append(i)
   end do
   call numbers%insert(2, -1)
   if (int_size(numbers) /= 4) error stop 'integer list size'
   if (any([(numbers%get(i), i=1,4)] /= [1,-1,2,3])) error stop 'integer list contents'
   if (numbers%find(2) /= 3 .or. numbers%find(99) /= 0) error stop 'integer search'
   print '(a,4(i0,1x))', 'Integer list: ', (numbers%get(i), i=1,int_size(numbers))
   call numbers%delete(2)
   if (int_size(numbers) /= 3) error stop 'integer deletion size'
   if (any([(numbers%get(i), i=1,3)] /= [1,2,3])) error stop 'integer deletion contents'

   call words%append('one')
   call words%append('two')
   call words%append('three')
   call words%insert(2, 'five')
   if (string_size(words) /= 4) error stop 'string list size'
   if (words%get(1) /= 'one' .or. words%get(2) /= 'five' .or. &
       words%get(3) /= 'two' .or. words%get(4) /= 'three') error stop 'string list contents'
   if (words%find('two') /= 3 .or. words%find('missing') /= 0) error stop 'string search'
   print '(a)', 'String list:'
   do i = 1, string_size(words)
      print '(2x,i0,2a)', i, ': ', words%get(i)
   end do
   deallocate(numbers, words)
   print '(a)', 'PASS fycollections'
end program typed_lists
