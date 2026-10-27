program main
   use forgex, only: operator(.match.), operator(.in.), regex
   implicit none
   character(:), allocatable :: number
   if (.not. ('[A-Z]{2}[0-9]{3}' .match. 'AB123')) error stop 'identifier not matched'
   if ('[A-Z]{2}[0-9]{3}' .match. 'AB12') error stop 'invalid identifier accepted'
   call regex('[0-9]+','sample=128',number)
   if (number /= '128') error stop 'incorrect extracted number'
   print *, 'Extracted sample count: ', number
   print *, 'PASS forgex'
end program
