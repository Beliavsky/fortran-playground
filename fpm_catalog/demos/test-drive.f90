program main
   use testdrive, only: error_type, check
   implicit none
   type(error_type), allocatable :: error
   call check(error, 2 + 2, 4)
   if (allocated(error)) error stop 'assertion failed'
   print *, 'PASS test-drive'
end program main
