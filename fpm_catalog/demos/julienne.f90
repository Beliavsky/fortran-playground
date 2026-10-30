! Uses Julienne's documented comparison idioms.
program main
   use julienne_m, only: test_diagnosis_t, operator(.approximates.), operator(.within.), &
      operator(.equalsExpected.), operator(//)
   implicit none
   type(test_diagnosis_t) :: numerical, exact, intentional_failure
   character(len=:), allocatable :: message

   numerical = (22.0/7.0 .approximates. acos(-1.0) .within. 0.002)
   exact = (sum([1,2,3]) .equalsExpected. 6)
   if (.not. numerical%test_passed()) error stop 'numerical comparison failed'
   if (.not. exact%test_passed()) error stop 'integer comparison failed'
   print *, 'Approximate and exact comparisons passed'

   ! Inspect a deliberately failing diagnosis without terminating the program.
   intentional_failure = (1 .equalsExpected. 2) // ' (deliberate demonstration)'
   if (intentional_failure%test_passed()) error stop 'failed comparison reported success'
   message = intentional_failure%diagnostics_string()
   if (len_trim(message) == 0) error stop 'missing failure diagnostic'
   if (index(message, 'deliberate demonstration') == 0) error stop 'missing appended diagnostic'
   print '(a)', 'Expected failure diagnostic: '//message
   print *, 'PASS julienne'
end program
