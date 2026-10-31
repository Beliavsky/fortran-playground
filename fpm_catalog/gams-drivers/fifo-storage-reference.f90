! Independent API consumer; MIT: licenses/data-kinds-drivers-MIT.txt.
program fifo_reference
   use fifo_queue, only: fifo,new_fifo_queue
   use, intrinsic :: iso_c_binding, only: c_int64_t,c_sizeof,c_ptr,c_f_pointer,c_associated
   implicit none
   type, bind(C) :: record
      integer(c_int64_t) :: serial,checksum
   end type record
   type(fifo) :: queue,other
   type(record), target :: input
   type(record) :: model(200),sentinel
   type(c_ptr) :: memory
   integer :: head,tail,cycle,i
   interface
      subroutine c_free(pointer) bind(C,name='free')
         import c_ptr
         type(c_ptr), value :: pointer
      end subroutine c_free
   end interface
   queue = new_fifo_queue(c_sizeof(input))
   other = new_fifo_queue(c_sizeof(input))
   sentinel = record(-999_c_int64_t,12345_c_int64_t)
   input = sentinel
   call other%push(input)
   input = record(0_c_int64_t,0_c_int64_t)
   head = 0
   tail = 0
   call count_check()
   do cycle = 1,3
      do i = 1,40
         call push_check()
      end do
      do i = 1,17
         call pop_check()
      end do
      do i = 1,13
         call push_check()
      end do
      do while (head < tail)
         call pop_check()
      end do
      if (queue%pop(memory)) error stop 'empty queue returned an item'
      if (c_associated(memory)) error stop 'empty pop pointer must be null'
      if (other%count() /= 1) error stop 'independent queue changed'
      print '(a,i0,a,i0,a)', 'Cycle ',cycle,': ',tail,' cumulative copied records checked; queue drained.'
   end do
   call extract(other,sentinel)
   if (other%count() /= 0 .or. .not. other%is_empty()) error stop 'secondary final state'
   call queue%destroy()
   call other%destroy()
   if (tail /= 159 .or. head /= tail) error stop 'reference model count'
   print '(a)', '160 records checked: interleaved FIFO order, copied values, empty/refill behavior, independent queues.'
   print '(a)', 'PASS fifo-storage-reference'
contains
   subroutine count_check()
      if (queue%count() /= tail-head) error stop 'reference queue count'
      if (queue%is_empty() .neqv. (tail == head)) error stop 'reference empty state'
   end subroutine count_check
   subroutine push_check()
      tail = tail+1
      model(tail) = record(int(tail,c_int64_t),int(tail*tail-7*tail,c_int64_t))
      input = model(tail)
      call queue%push(input)
      ! The queued record must survive overwriting the caller's storage.
      input = record(-1_c_int64_t,-1_c_int64_t)
      call count_check()
   end subroutine push_check
   subroutine pop_check()
      head = head+1
      call extract(queue,model(head))
      call count_check()
   end subroutine pop_check
   subroutine extract(which,expected)
      type(fifo), intent(inout) :: which
      type(record), intent(in) :: expected
      type(record), pointer :: output
      type(c_ptr) :: allocation
      if (.not. which%pop(allocation)) error stop 'early empty queue'
      if (.not. c_associated(allocation)) error stop 'null payload'
      call c_f_pointer(allocation,output)
      if (output%serial /= expected%serial .or. output%checksum /= expected%checksum) error stop 'copied FIFO record'
      ! Payloads were allocated with malloc; free each before destroying its empty queue.
      call c_free(allocation)
      nullify(output)
   end subroutine extract
end program fifo_reference
