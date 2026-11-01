! Independent MIT consumer; see licenses/statistics-services-ten-drivers-MIT.txt.
program main
   use assert_m, only: assert
   implicit none
   character(2048) :: executable
   character(512) :: line
   integer :: n,status,exit_code,length,unit,value
   logical :: found
   if(command_argument_count()>0) then
      call assert(.false.,'checked-assertion-enforcement-marker')
      print '(a)', 'Unexpected return from false assertion'
      stop
   end if
   do n=-32,32
      value=checked_square(n)
      if(value/=n*n) error stop 'Passing contract changed value'
   end do
   call get_command_argument(0,executable,length=length,status=status)
   if(status/=0.or.length>len(executable)) error stop 'Executable path'
   call execute_command_line('"'//trim(executable)//'" --expected-failure > assertion.log 2>&1', &
      cmdstat=status,exitstat=exit_code)
   if(status/=0.or.exit_code==0) error stop 'False assertion did not terminate child'
   found=.false.
   open(newunit=unit,file='assertion.log',status='old',action='read')
   do
      read(unit,'(a)',iostat=status) line
      if(status<0) exit
      if(status/=0) error stop 'Assertion log'
      if(index(line,'Unexpected return')>0) error stop 'Assertion was ignored'
      if(index(line,'checked-assertion-enforcement-marker')>0) found=.true.
   end do
   close(unit,status='delete')
   if(.not.found) error stop 'Missing assertion diagnostic'
   print '(a)', '65 pure-contract calls; false assertion terminates a child with the required diagnostic'
   print '(a)', 'PASS assert-enforcement-reference'
contains
   pure function checked_square(n) result(value)
      integer,intent(in) :: n
      integer :: value
      call assert(abs(n)<=32,'Bounded square input')
      value=n*n
      call assert(value>=0,'Nonnegative square')
   end function
end program
