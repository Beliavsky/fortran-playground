program typed_command_line
   use iso_fortran_env, only: dp=>real64
   use argparse, only: argparser
   implicit none
   type(argparser)::arguments
   character(2048)::executable
   integer::command_status,exit_status,length,status
   ! The playground starts a main without arguments. Relaunch this executable
   ! once with a fixed example command line to exercise the real parser API.
   if(command_argument_count()==0) then
      call get_command_argument(0,executable,length=length,status=status)
      if(status/=0 .or. length>len(executable)) error stop 'Cannot obtain executable path'
      call execute_command_line('"'//trim(executable)//'" -t 4 --scale 0.25 --name demo --verbose', &
         exitstat=exit_status,cmdstat=command_status)
      if(command_status/=0 .or. exit_status/=0) error stop 'Example command line failed'
   else
      arguments=argparser('Checked scientific command-line options')
      call arguments%set_program_name('example')
      call arguments%add_option_integer('-t','--threads','Thread count',1)
      call arguments%add_option_double('-s','--scale','Scale factor',1.0_dp)
      call arguments%add_option_string('-n','--name','Run label','unnamed')
      call arguments%add_option_integer('-i','--iterations','Iteration count',20)
      call arguments%add_option_logical('-v','--verbose','Enable verbose output')
      call arguments%parse()
      if(arguments%get_option_integer('--threads')/=4) error stop 'Integer option mismatch'
      if(abs(arguments%get_option_double('--scale')-0.25_dp)>1.e-12_dp) error stop 'Real option mismatch'
      if(trim(arguments%get_option_string('--name'))/='demo') error stop 'String option mismatch'
      if(arguments%get_option_integer('--iterations')/=20) error stop 'Default option mismatch'
      if(.not.arguments%has_option('--verbose')) error stop 'Logical option mismatch'
      print '(a)', 'Parsed: -t 4 --scale 0.25 --name demo --verbose'
      print '(a)', 'threads=4, scale=0.25, name=demo; default iterations=20'
      print *, 'PASS argparse-f'
   end if
end program typed_command_line
