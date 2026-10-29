program main
   use fed, only: format, int, real, char, operator(//)
   implicit none
   character(64) :: row
   character(:), allocatable :: specification
   specification = format(int(4)//char()//real(8,3))
   write(row, specification) 12, ' ', 3.125
   if (trim(row) /= '  12    3.125') error stop 'numeric columns'
   print '(a)', 'Generated format: '//specification
   print '(a)', trim(row)
   write(row, format(int(6,6))) 42
   if (trim(row) /= '000042') error stop 'zero padding'
   print '(a)', 'Zero-padded integer: '//trim(row)
   print *, 'PASS fed'
end program
