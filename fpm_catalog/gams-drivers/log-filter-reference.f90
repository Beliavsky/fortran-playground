! Independent MIT consumer; see licenses/storage-ten-drivers-MIT.txt.
program main
   use pflogger
   implicit none
   class(Logger),pointer :: log
   character(512) :: line
   character(40) :: message
   integer :: unit,status,i,record,expected_i
   open(newunit=unit,file='checked-logging.yaml',status='new')
   write(unit,'(a)') 'schema_version: 1', 'formatters:', '  basic:', '    class: Formatter', &
      "    format: '%(name)a~: %(levelName)a~: %(message)a'", &
      'handlers:', '  file:', '    class: FileHandler', '    filename: checked.log', &
      '    formatter: basic', '    level: WARNING', 'loggers:', '  main:', &
      '    handlers: [file]', '    level: DEBUG'
   close(unit)
   call initialize()
   call logging%load_file('checked-logging.yaml',rc=status)
   if(status/=0) error stop 'Logger configuration'
   log=>logging%get_logger('main')
   do i=1,32
      write(message,'(a,i3.3)') 'record-',i
      call log%debug('hidden-debug')
      call log%info('hidden-info')
      call log%warning(trim(message))
      call log%error(trim(message))
   end do
   call logging%free()
   call finalize()
   open(newunit=unit,file='checked.log',status='old')
   record=0
   do
      read(unit,'(a)',iostat=status) line
      if(status<0) exit
      if(status/=0) error stop 'Log read'
      record=record+1
      expected_i=(record+1)/2
      write(message,'(a,i3.3)') 'record-',expected_i
      if(mod(record,2)==1) then
         if(trim(line)/='main: WARNING: '//trim(message)) error stop 'Warning record oracle'
      else
         if(trim(line)/='main: ERROR: '//trim(message)) error stop 'Error record oracle'
      end if
   end do
   if(record/=64) error stop 'Severity count'
   close(unit,status='delete')
   open(newunit=unit,file='checked-logging.yaml',status='old')
   close(unit,status='delete')
   print '(a)', '128 log calls; exact 64 ordered warning/error records, debug/info filtered'
   print '(a)', 'PASS log-filter-reference'
end program
