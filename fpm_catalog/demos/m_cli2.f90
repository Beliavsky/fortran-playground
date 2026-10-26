program main
   use M_CLI2, only: set_args, iget, sget
   implicit none
   ! Hosted runs have no extra arguments; this demonstrates the defaults.
   call set_args('--count 42 --title "Fortran"')
   if (iget('count') /= 42) error stop 'incorrect integer option'
   if (sget('title') /= 'Fortran') error stop 'incorrect string option'
   print *, 'count =', iget('count'), ' title = ', sget('title')
   print *, 'PASS m_cli2'
end program main
