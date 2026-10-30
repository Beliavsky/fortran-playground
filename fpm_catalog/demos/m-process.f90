program main
   use M_process, only: streampointer, process_open_read, process_readline, process_close
   implicit none
   type(streampointer) :: stream
   character(len=256) :: line
   integer :: status, read_status, value, i

   call process_open_read("printf '7\n11\n'", stream, status)
   if (status /= 0) error stop 'pipe open failed'
   do i=1, 2
      call process_readline(line, stream, status)
      if (status /= 0) error stop 'pipe read failed'
      read(line, *, iostat=read_status) value
      if (read_status /= 0) error stop 'invalid pipe output'
      if (value /= 4*i+3) error stop 'unexpected pipe value'
      print '(a,i0)', 'Read from subprocess: ', value
   end do
   call process_readline(line, stream, status)
   if (status == 0) error stop 'expected end of pipe'
   call process_close(stream, status)
   if (status /= 0) error stop 'subprocess did not exit successfully'
   print *, 'End of output and subprocess status checked'
   print *, 'PASS m-process'
end program
