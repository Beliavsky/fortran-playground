program main
   use prime_numbers, only: primes, is_prime
   implicit none
   integer, allocatable :: values(:)
   values = primes(30)
   if (size(values) /= 10) error stop 'incorrect prime count'
   if (any(values /= [2,3,5,7,11,13,17,19,23,29])) error stop 'incorrect primes'
   if (.not. is_prime(97) .or. is_prime(91)) error stop 'incorrect primality test'
   print *, 'Primes through 30:', values
   print *, 'PASS fortran-primes'
end program
