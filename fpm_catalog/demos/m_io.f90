program main
   use M_io, only: fileread
   implicit none
   character(:), allocatable :: lines(:)
   integer :: unit
   open(newunit=unit,file='message.txt',status='replace')
   write(unit,'(a)') 'Fortran file input'
   close(unit)
   call fileread('message.txt',lines)
   if (.not. allocated(lines)) error stop 'read failed'
   if (size(lines) /= 1) error stop 'incorrect line count'
   if (trim(lines(1)) /= 'Fortran file input') error stop 'incorrect text'
   print *, trim(lines(1))
   print *, 'PASS m_io'
end program main
