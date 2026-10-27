program main
   use shlex_module, only: split
   implicit none
   character(:), allocatable :: words(:)
   words = split('simulate --title "heat flow"')
   if (size(words) /= 3) error stop 'incorrect token count'
   if (words(3) /= 'heat flow') error stop 'quoted text split incorrectly'
   print *, 'Third argument: ', trim(words(3))
   print *, 'PASS fortran-shlex'
end program
