! Assertions are enabled in this precompiled library with -DASSERTIONS=1.
program main
   use assert_m, only: assert
   implicit none
   real :: value
   value = checked_sqrt(4.0)
   print '(a,f6.2)', 'checked_sqrt(4) = ', value
   if (abs(value-2.0) > 1.0e-6) error stop 'Incorrect square root'
   print '(a)', 'Precondition and postcondition checks passed in a pure function.'
   print '(a)', 'PASS berkeley-assert'
contains
   pure function checked_sqrt(x) result(y)
      real, intent(in) :: x
      real :: y
      call assert(x >= 0.0, 'Square-root input must be nonnegative')
      y = sqrt(x)
      call assert(abs(y*y-x) < 1.0e-6, 'Square-root residual must be small')
   end function checked_sqrt
end program main
