! All files are temporary and stay inside the program's working directory.
program main
   use os, only: mkdir, rmdir, rename, unlink, os_name, os_id, OS_LINUX
   use os_path, only: join, exists, isdir, isfile, getsize, basename, dirname, normpath
   implicit none
   integer :: status, unit
   character(:), allocatable :: folder, filename, renamed
   if (os_id /= OS_LINUX .or. os_name /= 'Linux') error stop 'Linux configuration failed'
   folder = join('os-demo', 'nested')
   filename = join(folder, 'sample.txt')
   renamed = join(folder, 'renamed.txt')
   call mkdir('os-demo', stat=status)
   if (status /= 0) error stop 'mkdir failed'
   call mkdir(folder, stat=status)
   if (status /= 0 .or. .not. isdir(folder)) error stop 'nested directory failed'
   open(newunit=unit, file=filename, access='stream', form='unformatted', status='new', iostat=status)
   if (status /= 0) error stop 'open failed'
   write(unit) 'Hello Fortran!'
   close(unit)
   if (.not. exists(filename) .or. .not. isfile(filename)) error stop 'file metadata failed'
   if (getsize(filename) /= 14) error stop 'file size failed'
   if (basename(filename) /= 'sample.txt') error stop 'basename failed'
   if (dirname(filename) /= folder) error stop 'dirname failed'
   if (normpath('os-demo/./nested/../nested') /= folder) error stop 'path normalization failed'
   print '(a,a)', 'Operating system: ', os_name
   print '(a,a,a,i0)', 'Created ', filename, ', bytes: ', getsize(filename)
   call rename(filename, renamed, stat=status)
   if (status /= 0) error stop 'rename failed'
   if (exists(filename) .or. .not. exists(renamed)) error stop 'rename metadata failed'
   call unlink(renamed, stat=status)
   if (status /= 0 .or. exists(renamed)) error stop 'unlink failed'
   call rmdir(folder, stat=status)
   if (status /= 0) error stop 'nested rmdir failed'
   call rmdir('os-demo', stat=status)
   if (status /= 0 .or. exists('os-demo')) error stop 'cleanup failed'
   print '(a)', 'PASS stdlib-os'
end program main
