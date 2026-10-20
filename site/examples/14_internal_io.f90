! Example: Text: strings and internal I/O
! Adapted from https://github.com/Beliavsky/FortranTip/blob/main/internal_read_write.f90
! Original internal I/O tip credited to urbanjost in FortranTip.
! Try changing text to 'not a number' to exercise iostat handling.
program strings_and_internal_io
   use, intrinsic :: iso_fortran_env, only: real64
   implicit none
   character(len=32) :: text, formatted
   character(len=*), parameter :: name = 'Fortran'
   real(real64) :: value
   integer :: ios
   text = '123.4e2'
   read(text,*,iostat=ios) value
   if (ios /= 0) then
      print '(a)', 'Could not read a number: '//trim(text)
   else
      write(formatted,'(f10.2)') value
      print '(a)', 'Parsed number: '//trim(adjustl(formatted))
   end if
   print '(a)', 'Greeting: Hello, '//name//'!'
   print '(a)', 'Substring: '//name(1:4)
end program strings_and_internal_io
