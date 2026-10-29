program main
   use sll_module, only: sll, iterator, sll_finalizer, iterator_finalizer
   implicit none
   type(sll) :: list
   type(iterator) :: iter
   class(*), pointer :: item
   integer :: n, capacity

   call list%push_back(7)
   call list%push_back(2.5)
   if (list%size() /= 2) error stop 'list size'
   capacity = list%size(.true.)
   iter = iterator(list)
   n = 0
   do while (iter%next(item))
      n = n + 1
      select type (item)
      type is (integer)
         if (n /= 1 .or. item /= 7) error stop 'integer element'
         print '(a,i0)', 'Integer: ', item
      type is (real)
         if (n /= 2 .or. item /= 2.5) error stop 'real element'
         print '(a,f4.1)', 'Real: ', item
      class default
         error stop 'unexpected type'
      end select
   end do
   if (n /= 2) error stop 'iteration count'
   call iterator_finalizer(iter)
   call list%empty()
   if (.not. list%is_empty()) error stop 'empty'
   call list%push_back(9)
   if (list%size() /= 1) error stop 'reused size'
   if (list%size(.true.) /= capacity) error stop 'capacity changed'
   iter = iterator(list)
   if (.not. iter%next(item)) error stop 'missing reused element'
   select type (item)
   type is (integer)
      if (item /= 9) error stop 'reused value'
   class default
      error stop 'reused type'
   end select
   print '(a,i0)', 'Capacity retained after emptying and reusing: ', capacity
   call iterator_finalizer(iter)
   call sll_finalizer(list)
   print '(a)', 'PASS slinked-list'
end program main
