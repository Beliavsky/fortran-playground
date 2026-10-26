program main
   use argv_module, only: argv
   implicit none
   character(:), allocatable :: executable
   ! No extra command-line arguments are supplied by the hosted playground.
   executable = argv(0)
   if (len(executable) == 0) error stop 'missing executable name'
   print *, 'Executable:', executable
   print *, 'PASS argv-fortran'
end program main
