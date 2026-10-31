! Minimal pinned-package reproducer; run with an external timeout.
program main
   use iso_fortran_env, only: int64, output_unit
   use prime_numbers, only: is_prime
   implicit none
   logical :: answer
   print '(a)', 'Checking is_prime(3215031751_int64)'
   flush(output_unit)
   answer = is_prime(3215031751_int64)
   print '(a,l1)', 'Returned: ', answer
   if (answer) error stop '3215031751 = 151 * 751 * 28351 is composite'
end program
