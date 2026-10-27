program main
   use regex_module, only: regex
   implicit none
   integer :: position, length
   position = regex('temperature=273 K', '[0-9]+', length)
   if (position /= 13 .or. length /= 3) error stop 'incorrect match'
   print *, 'Number starts at character', position, 'with length', length
   print *, 'PASS fortran-regex'
end program
