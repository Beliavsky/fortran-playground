! GAMS B: prime enumeration and primality, checked against independent trial division.
! Author API patterns: perazz/fortran-primes test/test_primes.f90 at the catalog pin.
! See licenses/fortran-primes-MIT.txt and the upstream source's additional notices.
program main
   use iso_fortran_env, only: int32, int64
   use prime_numbers, only: primes, is_prime
   implicit none
   integer(int32), allocatable :: actual(:), expected(:)
   integer(int32) :: n, k, reference(1000)
   integer(int64), parameter :: large_cases(*) = [ &
      -2_int64, 0_int64, 1_int64, 2_int64, 2147483647_int64, &
      3215031751_int64, 10000000019_int64, 10000000021_int64]

   k = 0
   do n = -20, 1000
      if (is_prime(n) .neqv. trial_prime(int(n, int64))) then
         print '(a,i0)', 'Primality mismatch for ', n
         error stop 'int32 primality check'
      end if
      if (trial_prime(int(n, int64))) then
         k = k + 1
         reference(k) = n
      end if
   end do
   expected = reference(:k)
   actual = primes(1000_int32)
   if (size(actual) /= size(expected)) error stop 'prime list size'
   if (any(actual /= expected)) error stop 'prime list values'
   if (size(actual) /= 168 .or. sum(actual) /= 76127) error stop 'known count and sum'
   print '(a,i0,a,i0)', 'Primes through 1000: count = ', size(actual), '; sum = ', sum(actual)

   expected = pack(reference(:k), reference(:k) >= 100 .and. reference(:k) <= 200)
   actual = primes(100_int32, 200_int32)
   if (size(actual) /= size(expected)) error stop 'bounded list size'
   if (any(actual /= expected)) error stop 'bounded list values'
   print '(a,*(1x,i0))', 'Primes in [100,200]:', actual
   actual = primes(1_int32)
   if (size(actual) /= 0) error stop 'no primes below two'
   actual = primes(10_int32, 2_int32)
   if (size(actual) /= 0) error stop 'reversed range'

   do k = 1, size(large_cases)
      if (is_prime(large_cases(k)) .neqv. trial_prime(large_cases(k))) then
         print '(a,i0)', 'Primality mismatch for ', large_cases(k)
         error stop 'int64 primality check'
      end if
      print '(a,i0,a,l1)', 'is_prime(', large_cases(k), ') = ', is_prime(large_cases(k))
   end do
   print '(a)', 'Checked 1021 int32 cases, 8 int64 cases, and enumerated prime lists.'
   print '(a)', 'PASS primes-trial-division'
contains
   logical function trial_prime(value) result(prime)
      integer(int64), intent(in) :: value
      integer(int64) :: divisor
      prime = .false.
      if (value < 2) return
      divisor = 2
      ! Division in the bound avoids squaring a potentially large divisor.
      do while (divisor <= value / divisor)
         if (modulo(value, divisor) == 0) return
         divisor = divisor + 1
      end do
      prime = .true.
   end function
end program
