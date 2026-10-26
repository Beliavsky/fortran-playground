program main
   use json_module, only: json_file
   implicit none
   type(json_file) :: document
   integer :: answer
   logical :: found
   call document%initialize()
   call document%load_from_string('{"answer":42}')
   call document%get('answer', answer, found)
   if (.not. found) error stop 'missing value'
   if (answer /= 42) error stop 'incorrect JSON value'
   print *, 'answer =', answer
   call document%destroy()
   print *, 'PASS json-fortran'
end program main
