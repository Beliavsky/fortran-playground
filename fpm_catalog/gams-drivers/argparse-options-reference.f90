! Independent MIT consumer; see licenses/workflows-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64
   use argparse, only: argparser
   implicit none
   type(argparser) :: options
   character(2048) :: executable
   character(20) :: case_text,threads_text,scale_text
   character(40) :: label
   character(:),allocatable :: command
   integer :: n,status,exit_code,length
   if(command_argument_count()==0) then
      call get_command_argument(0,executable,length=length,status=status)
      if(status/=0.or.length>len(executable)) error stop 'Executable path'
      do n=1,12
         write(case_text,'(i0)') n
         write(threads_text,'(i0)') 2*n+1
         write(scale_text,'(f10.3)') real(n-7,real64)/8
         command='"'//trim(executable)//'" --case '//trim(case_text)
         if(mod(n,2)==0) then
            command=command//' --threads '
         else
            command=command//' -t '
         end if
         command=command//trim(threads_text)//' --scale '//trim(adjustl(scale_text))// &
            ' --name "case '//trim(case_text)//'"'
         if(mod(n,2)==0) command=command//' --verbose'
         call execute_command_line(command,cmdstat=status,exitstat=exit_code)
         if(status/=0.or.exit_code/=0) error stop 'Child parser check'
      end do
      print '(a)', '12 child invocations; 72 typed/default/flag references, short and long option names'
      print '(a)', 'PASS argparse-options-reference'
   else
      call get_command_argument(2,case_text)
      read(case_text,*) n
      options=argparser('Checked parser')
      call options%add_option_integer('-c','--case','Fixture',0)
      call options%add_option_integer('-t','--threads','Threads',1)
      call options%add_option_double('-s','--scale','Scale',1._real64)
      call options%add_option_string('-n','--name','Label','unset')
      call options%add_option_integer('-i','--iterations','Iterations',37)
      call options%add_option_logical('-v','--verbose','Verbose')
      call options%parse()
      write(label,'(a,i0)') 'case ',n
      if(options%get_option_integer('--case')/=n) error stop 'Case'
      if(options%get_option_integer('--threads')/=2*n+1) error stop 'Integer'
      if(options%get_option_double('--scale')/=real(n-7,real64)/8) error stop 'Real'
      if(trim(options%get_option_string('--name'))/=trim(label)) error stop 'Quoted string'
      if(options%get_option_integer('--iterations')/=37) error stop 'Default'
      if(options%has_option('--verbose').neqv.(mod(n,2)==0)) error stop 'Logical flag'
   end if
end program
