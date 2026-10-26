program main
   use popen_module, only: get_command_as_string
   implicit none
   character(:), allocatable :: output
   output = get_command_as_string('printf 42')
   if (trim(output) /= '42') error stop 'incorrect subprocess output'
   print *, 'Captured output:', output
   print *, 'PASS popen-fortran'
end program main
