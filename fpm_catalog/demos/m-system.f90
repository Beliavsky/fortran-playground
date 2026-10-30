program main
   use M_system, only: system_mkdir, system_isdir, system_isreg, system_remove, system_rmdir, &
      R_USR, W_USR, X_USR
   implicit none
   integer :: status, unit, value
   logical :: exists

   status = system_mkdir('playground-demo', iany([R_USR, W_USR, X_USR]))
   if (status /= 0) error stop 'mkdir failed'
   if (.not. system_isdir('playground-demo')) error stop 'directory not found'
   open(newunit=unit, file='playground-demo/value.txt', status='new', action='write', iostat=status)
   if (status /= 0) error stop 'file creation failed'
   write(unit, *) 42
   close(unit)
   if (.not. system_isreg('playground-demo/value.txt')) error stop 'regular file not found'
   open(newunit=unit, file='playground-demo/value.txt', status='old', action='read', iostat=status)
   if (status /= 0) error stop 'file open failed'
   read(unit, *, iostat=status) value
   close(unit)
   if (status /= 0 .or. value /= 42) error stop 'file contents mismatch'
   print '(a,i0)', 'Created a directory and regular file; read back ', value
   status = system_remove('playground-demo/value.txt')
   if (status /= 0) error stop 'remove failed'
   inquire(file='playground-demo/value.txt', exist=exists)
   if (exists) error stop 'file still exists'
   status = system_rmdir('playground-demo')
   if (status /= 0) error stop 'rmdir failed'
   if (system_isdir('playground-demo')) error stop 'directory still exists'
   print *, 'Cleanup verified'
   print *, 'PASS m-system'
end program
