program main
   use iso_fortran_env, only: real64
   use errstat, only: error_stat_type, catch_error, set_success, error_occurred
   implicit none
   type(error_stat_type) :: status
   real(real64) :: value

   value = reciprocal(4.0_real64, status)
   if (error_occurred(status)) error stop 'unexpected error'
   if (value /= 0.25_real64) error stop 'reciprocal'
   print '(a,f6.2)', '1 / 4 = ', value
   value = reciprocal(0.0_real64, status)
   if (.not. error_occurred(status)) error stop 'zero not rejected'
   if (status%get_status() /= 1) error stop 'error code'
   if (status%get_message() /= 'Cannot divide by zero') error stop 'error message'
   print '(a,i0,2a)', 'Status ', status%get_status(), ': ', status%get_message()
   value = reciprocal(2.0_real64, status)
   if (error_occurred(status)) error stop 'error not cleared'
   if (value /= 0.5_real64) error stop 'recovery'
   print '(a)', 'A subsequent valid call clears the error.'
   print '(a)', 'PASS errstat'
contains
   function reciprocal(x, status) result(y)
      real(real64), intent(in) :: x
      type(error_stat_type), intent(out) :: status
      real(real64) :: y
      y = 0
      if (x == 0) then
         call catch_error(1, 'Cannot divide by zero', status)
         return
      end if
      y = 1 / x
      call set_success(status)
   end function reciprocal
end program main
