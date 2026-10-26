module functions
   use numdiff_kinds_module, only: wp
   use diff_module, only: diff_func
   implicit none
contains
   function square(me,x) result(y)
      class(diff_func), intent(inout) :: me
      real(wp), intent(in) :: x
      real(wp) :: y
      y = x*x
   end function
end module
program main
   use functions
   implicit none
   type(diff_func) :: derivative
   real(wp) :: value, error
   integer :: status
   call derivative%set_function(square)
   call derivative%compute_derivative(1, 2.0_wp, 0.0_wp, 4.0_wp, 1.e-10_wp, &
      -epsilon(1.0_wp), value, error, status)
   if (status /= 0 .or. abs(value-4.0_wp) > 1.e-7_wp) error stop 'incorrect derivative'
   print *, 'Derivative of x squared at 2:', value
   print *, 'PASS numdiff'
end program main
