! Independent MIT consumer; see licenses/workflows-ten-drivers-MIT.txt.
program main
   use M_process, only: streampointer,process_open_read,process_readline,process_close
   implicit none
   type(streampointer) :: pipe
   character(40) :: token
   character(256) :: line
   character(:),allocatable :: command
   integer :: trial,i,n,status,value,ios,total
   total=0
   do trial=1,4
      n=17*trial
      command="printf '%s\n'"
      do i=1,n
         write(token,'(i0)') i*i-100
         command=command//" '"//trim(token)//"'"
      end do
      call process_open_read(command,pipe,status)
      if(status/=0) error stop 'Read pipe open'
      do i=1,n
         call process_readline(line,pipe,status)
         if(status/=0) error stop 'Early pipe end'
         read(line,*,iostat=ios) value
         if(ios/=0.or.value/=i*i-100) error stop 'Pipe record oracle'
         total=total+1
      end do
      call process_readline(line,pipe,status)
      if(status==0) error stop 'Extra pipe output'
      call process_close(pipe,status)
      if(status/=0) error stop 'Process close status'
   end do
   print '(a,i0)', 'Four fixed local printf pipes; exact ordered records with EOF/status checks: ',total
   print '(a)', 'PASS process-lines-reference'
end program
