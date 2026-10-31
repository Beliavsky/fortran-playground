! Independent API consumer; MIT: licenses/products-status-drivers-MIT.txt.
program recovery_reference
   use errstat, only: error_stat_type,catch_error,set_success,error_occurred
   use, intrinsic :: iso_fortran_env, only: real64
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite,ieee_value,ieee_quiet_nan
   implicit none
   real(real64) :: numerator(9),denominator(9),value
   real(real64), parameter :: expected_values(*) = [1.5_real64,0._real64,2._real64,0._real64, &
      1._real64,0._real64,3._real64,0._real64,7._real64]
   integer, parameter :: codes(*) = [0,101,0,102,0,103,0,101,0]
   type(error_stat_type) :: status,saved
   character(:), allocatable :: message
   integer :: i
   numerator = [9._real64,9._real64,16._real64,-1._real64,25._real64,0._real64,36._real64,4._real64,49._real64]
   numerator(6) = ieee_value(0._real64,ieee_quiet_nan)
   denominator = [4._real64,0._real64,4._real64,1._real64,25._real64,1._real64,4._real64,-0._real64,1._real64]
   do i = 1,size(codes)
      value = safe_ratio_root(numerator(i),denominator(i),status)
      if (status%get_status() /= codes(i)) error stop 'expected status code'
      if (error_occurred(status) .neqv. (codes(i) /= 0)) error stop 'expected error flag'
      select case(codes(i))
      case(0)
         message = 'ok'
      case(101)
         message = 'zero denominator'
      case(102)
         message = 'negative radicand'
      case(103)
         message = 'nonfinite input'
      end select
      if (status%get_message() /= message) error stop 'exact error or recovery message'
      if (.not. ieee_is_finite(value) .or. value /= expected_values(i)) error stop 'driver arithmetic result'
      print '(a,i0,a,i0,2a)', 'Call ',i,': status=',status%get_status(),' message=',status%get_message()
   end do
   call catch_error(701,'original',status)
   saved = status
   call status%append_message('context')
   if (status%get_message() /= 'original - context') error stop 'appended error context'
   if (saved%get_message() /= 'original' .or. saved%get_status() /= 701) error stop 'independent status copy'
   call set_success(status,'recovered')
   if (error_occurred(status) .or. status%get_status() /= 0) error stop 'explicit recovery status'
   if (status%get_message() /= 'recovered') error stop 'explicit recovery message'
   if (.not. error_occurred(saved) .or. saved%get_message() /= 'original') error stop 'copy survived recovery'
   call status%initialize()
   if (error_occurred(status) .or. status%get_message() /= '') error stop 'status initialization reset'
   print '(a)', 'Nine success/failure/recovery calls, copied statuses, appended context and explicit reset checked.'
   print '(a)', 'PASS errstat-recovery-reference'
contains
   function safe_ratio_root(a,b,state) result(y)
      real(real64), intent(in) :: a,b
      type(error_stat_type), intent(out) :: state
      real(real64) :: y
      y = 0._real64
      if (.not. ieee_is_finite(a) .or. .not. ieee_is_finite(b)) then
         call catch_error(103,'nonfinite input',state)
      else if (b == 0._real64) then
         call catch_error(101,'zero denominator',state)
      else if (a/b < 0._real64) then
         call catch_error(102,'negative radicand',state)
      else
         y = sqrt(a/b)
         call set_success(state,'ok')
      end if
   end function safe_ratio_root
end program recovery_reference
