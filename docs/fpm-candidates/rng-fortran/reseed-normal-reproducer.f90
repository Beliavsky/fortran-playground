! In this pinned revision, set_seed does not discard normal()'s cached second draw.
! The selected demo uses fresh generators for its reproducibility check.
program reseed_normal
   use iso_fortran_env, only: int64, real64
   use m_random, only: rng_t
   implicit none
   type(rng_t) :: used, fresh
   integer(int64), parameter :: seed(2) = [123456789_int64, 987654321_int64]
   real(real64) :: first, after_reset, expected

   call used%set_seed(seed)
   first = used%normal()
   call used%set_seed(seed)
   after_reset = used%normal()
   call fresh%set_seed(seed)
   expected = fresh%normal()
   if (abs(first-expected) > 1.0e-14_real64) error stop 'fresh sequence mismatch'
   if (abs(after_reset-expected) < 1.0e-12_real64) error stop 'limitation not reproduced'
   print '(a,f12.7)', 'Fresh first normal: ', expected
   print '(a,f12.7)', 'Normal after resetting a used generator: ', after_reset
   print '(a)', 'REPRODUCED cached normal survives set_seed'
end program reseed_normal
