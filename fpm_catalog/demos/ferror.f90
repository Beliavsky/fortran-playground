program main
   use ferror, only: errors
   implicit none
   type(errors) :: handler
   call handler%set_exit_on_error(.false.)
   call handler%set_suppress_printing(.true.)
   call handler%report_error('read_sample','Sample count must be positive',42)
   if (.not. handler%has_error_occurred()) error stop 'missing error'
   if (handler%get_error_flag() /= 42) error stop 'incorrect error code'
   print *, 'Handled error:', handler%get_error_flag()
   call handler%reset_error_status()
   if (handler%has_error_occurred()) error stop 'error not reset'
   print *, 'PASS ferror'
end program
