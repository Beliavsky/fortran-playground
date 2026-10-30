! A serial logging configuration; only WARNING and ERROR should reach the file.
program main
   use pflogger
   implicit none
   class(Logger), pointer :: log
   integer :: unit, status, count
   character(512) :: line
   open(newunit=unit, file='logging.yaml', status='replace', action='write')
   write(unit,'(a)') 'schema_version: 1', 'formatters:', '  basic:', '    class: Formatter', &
      "    format: '%(name)a~: %(levelName)a~: %(message)a'", &
      'handlers:', '  checked_file:', '    class: FileHandler', '    filename: checked.log', &
      '    formatter: basic', '    level: WARNING', 'loggers:', '  main:', &
      '    handlers: [checked_file]', '    level: DEBUG'
   close(unit)
   call initialize()
   call logging%load_file('logging.yaml', rc=status)
   if (status /= 0) error stop 'Logging configuration failed'
   log => logging%get_logger('main')
   call log%debug('hidden-debug')
   call log%info('hidden-info')
   call log%warning('accepted-warning')
   call log%error('accepted-error')
   call logging%free()
   call finalize()
   open(newunit=unit, file='checked.log', status='old', action='read', iostat=status)
   if (status /= 0) error stop 'Log file was not created'
   count = 0
   do
      read(unit,'(a)',iostat=status) line
      if (status < 0) exit
      if (status > 0) error stop 'Log file read failed'
      count = count + 1
      if (index(line,'hidden-') /= 0) error stop 'Severity filtering failed'
      if (count == 1 .and. trim(line) /= 'main: WARNING: accepted-warning') error stop 'Warning record mismatch'
      if (count == 2 .and. trim(line) /= 'main: ERROR: accepted-error') error stop 'Error record mismatch'
      print '(a)', trim(line)
   end do
   close(unit, status='delete')
   if (count /= 2) error stop 'Wrong number of log records'
   open(newunit=unit, file='logging.yaml', status='old')
   close(unit, status='delete')
   print '(a)', 'PASS pflogger'
end program main
