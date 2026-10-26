program main
   use M_strings, only: upper
   implicit none
   if (upper('Fortran') /= 'FORTRAN') error stop 'incorrect conversion'
   print *, upper('Fortran strings')
   print *, 'PASS m_strings'
end program main
