! Independent MIT API consumer; see licenses/data-ten-drivers-MIT.txt.
program list_reference
   use sll_module, only: sll,iterator,sll_finalizer,iterator_finalizer
   implicit none
   type(sll), target :: list
   type(iterator) :: cursor
   class(*), pointer :: item
   integer :: cycle,i,n,counted,capacity,entries
   character(16) :: label,expected
   entries=0; capacity=0
   do cycle=1,20
      n=1+modulo(cycle*17,61)
      do i=1,n
         select case(modulo(i+cycle,3))
         case(0)
            call list%push_back(100*cycle-i)
         case(1)
            call list%push_back(real(i-cycle)/8)
         case(2)
            write(label,'(i0,a,i0)') cycle,':',i
            call list%push_back(label)
         end select
      end do
      if (list%size()/=n .or. list%is_empty()) error stop 'list size reference'
      cursor=iterator(list); counted=0
      do while(cursor%next(item))
         counted=counted+1; i=counted
         select type(item)
         type is (integer)
            if (modulo(i+cycle,3)/=0 .or. item/=100*cycle-i) error stop 'list integer reference'
         type is (real)
            if (modulo(i+cycle,3)/=1 .or. item/=real(i-cycle)/8) error stop 'list real reference'
         type is (character(*))
            write(expected,'(i0,a,i0)') cycle,':',i
            if (modulo(i+cycle,3)/=2 .or. item/=expected) error stop 'list character reference'
         class default
            error stop 'unexpected list dynamic type'
         end select
      end do
      if (counted/=n) error stop 'list iteration count'
      if (cursor%next(item)) error stop 'list exhausted iterator'
      entries=entries+counted
      call iterator_finalizer(cursor)
      call list%empty(); capacity=max(capacity,n)
      if (.not.list%is_empty() .or. list%size()/=0) error stop 'list clear reference'
      if (list%size(.true.)/=capacity) error stop 'retained list capacity'
   end do
   call sll_finalizer(list)
   if (.not.list%is_empty() .or. list%size(.true.)/=0) error stop 'list finalization reference'
   print '(a,i0)', '20 heterogeneous list growth/reuse cycles; typed element references: ',entries
   print '(a)', 'Integer/real/character order, dynamic type replacement, retained capacity and iterator exhaustion.'
   print '(a)', 'Empty-list iterator construction, mutation during iteration and pointer lifetime misuse unverified.'
   print '(a)', 'PASS linked-list-reference'
end program
