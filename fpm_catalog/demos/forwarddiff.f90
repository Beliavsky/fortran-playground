module example_functions
   use differentia, only: wp, derivative
   implicit none
contains
   function cubic(x) result(y)
      use differentia
      type(dual), intent(in) :: x
      type(dual) :: y
      y = x*x*x
   end function
end module example_functions

program main
   use example_functions, only: cubic
   use differentia, only: wp, derivative
   implicit none
   real(wp) :: value, slope
   call derivative(cubic, 2.0_wp, value, slope)
   if (abs(value-8.0_wp) > 1.e-12_wp) error stop 'incorrect value'
   if (abs(slope-12.0_wp) > 1.e-12_wp) error stop 'incorrect derivative'
   print *, 'x cubed and its derivative at x=2:', value, slope
   print *, 'PASS forwarddiff'
end program main
