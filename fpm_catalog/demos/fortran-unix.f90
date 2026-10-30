! Sandbox-local file metadata and removal using the author's POSIX bindings.
program main
   use unix
   implicit none
   character(*), parameter :: filename = 'playground-posix.txt'
   type(c_stat_t) :: info
   integer :: unit, status
   logical :: exists
   open(newunit=unit, file=filename, access='stream', form='unformatted', status='replace')
   write(unit) 'Fortran POSIX'
   close(unit)
   status = c_stat(filename // c_null_char, info)
   if (status /= 0) error stop 'stat failed'
   if (info%st_size /= 13) error stop 'Incorrect file size'
   print '(a,i0,a)', 'Created file: ', info%st_size, ' bytes'
   status = c_unlink(filename // c_null_char)
   if (status /= 0) error stop 'unlink failed'
   inquire(file=filename, exist=exists)
   if (exists) error stop 'File was not removed'
   print '(a)', 'Removed the temporary file.'
   print '(a)', 'PASS fortran-unix'
end program main
