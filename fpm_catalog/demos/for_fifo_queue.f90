program main
   use iso_c_binding, only: c_int64_t, c_sizeof, c_ptr, c_f_pointer, c_associated
   use fifo_queue, only: fifo, new_fifo_queue
   implicit none
   type(fifo) :: queue
   ! An 8-byte payload also keeps the following C pointer header aligned here.
   integer(c_int64_t), target :: input
   integer(c_int64_t), pointer :: output
   type(c_ptr) :: memory
   integer :: i
   interface
      subroutine c_free(pointer) bind(C, name='free')
         import c_ptr
         type(c_ptr), value :: pointer
      end subroutine
   end interface
   queue = new_fifo_queue(c_sizeof(input))
   do i = 1, 4
      input = 10*i
      call queue%push(input)
   end do
   if (queue%count() /= 4) error stop 'initial count'
   do i = 1, 4
      if (.not. queue%pop(memory)) error stop 'early empty queue'
      if (.not. c_associated(memory)) error stop 'null item'
      call c_f_pointer(memory, output)
      if (output /= 10*i) error stop 'FIFO order'
      print *, 'Popped:', output
      ! Items were allocated by C; release them with C free.
      call c_free(memory)
      nullify(output)
   end do
   if (.not. queue%is_empty()) error stop 'not empty'
   if (queue%count() /= 0) error stop 'final count'
   if (queue%pop(memory)) error stop 'extra item'
   call queue%destroy()
   print *, 'PASS for_fifo_queue'
end program
