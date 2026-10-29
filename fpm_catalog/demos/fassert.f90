program main
   use iso_fortran_env, only: real64
   use fassert, only: assert_equal, assert_approx_equal, expect_equal
   implicit none
   logical :: passed
   character(:), allocatable :: message

   call assert_equal(2 + 3, 5, 'integer addition')
   call assert_equal([1, 4, 9], [1, 4, 9], 'integer array')
   call assert_approx_equal(sqrt(2.0_real64)**2, 2.0_real64, 'square root round trip', &
      tolerance=1.0e-12_real64)
   ! Capture an intentional failure so the program can inspect it and continue.
   call expect_equal(2 + 3, 6, 'intentional mismatch', passed, output_message=message)
   if (passed) error stop 'mismatch not detected'
   if (index(message, 'intentional mismatch') == 0) error stop 'missing diagnostic'
   print '(a)', 'Scalar, array and approximate comparisons passed.'
   print '(a)', 'Captured expected failure:'
   print '(a)', message
   print '(a)', 'PASS fassert'
end program main
