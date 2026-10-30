program main
   use iso_fortran_env, only: int64, real64
   use ieee_arithmetic, only: ieee_is_finite
   use m_random, only: rng_t
   implicit none
   integer, parameter :: n = 10000
   type(rng_t) :: generator, replay
   integer(int64), parameter :: seed(2) = [123456789_int64, 987654321_int64]
   real(real64) :: uniform(n), normal(n), poisson(n), pair(2), sphere(3), repeated
   integer :: i, count

   call generator%set_seed(seed)
   call replay%set_seed(seed)
   do i = 1, n
      uniform(i) = generator%unif_01()
      repeated = replay%unif_01()
      if (uniform(i) /= repeated) error stop 'seed reproducibility'
   end do
   ! The implementation returns [0,1), despite the older README saying (0,1].
   if (any(uniform < 0) .or. any(uniform >= 1)) error stop 'uniform range'
   do i = 1, n
      normal(i) = generator%normal()
      count = generator%poisson(4.0_real64)
      if (count < 0) error stop 'negative Poisson count'
      poisson(i) = real(count, real64)
   end do
   if (.not. all(ieee_is_finite(normal))) error stop 'nonfinite normal'
   if (abs(sum(uniform)/n - 0.5_real64) > 0.03_real64) error stop 'uniform mean'
   if (abs(sum(normal)/n) > 0.08_real64) error stop 'normal mean'
   if (abs(sum(normal**2)/n - 1) > 0.12_real64) error stop 'normal second moment'
   if (abs(sum(poisson)/n - 4) > 0.2_real64) error stop 'Poisson mean'
   pair = generator%circle(1.0_real64)
   sphere = generator%sphere(1.0_real64)
   if (abs(sum(pair**2)-1) > 1.0e-12_real64) error stop 'unit circle'
   if (abs(sum(sphere**2)-1) > 1.0e-12_real64) error stop 'unit sphere'
   print '(a,i0)', 'Reproducible uniform samples: ', n
   print '(a,f8.4)', 'Uniform mean (expected 0.5): ', sum(uniform)/n
   print '(a,f8.4)', 'Normal mean (expected 0): ', sum(normal)/n
   print '(a,f8.4)', 'Normal second moment (expected 1): ', sum(normal**2)/n
   print '(a,f8.4)', 'Poisson mean (expected 4): ', sum(poisson)/n
   print '(a)', 'These are small deterministic smoke checks, not a randomness certification.'
   print '(a)', 'PASS rng-fortran'
end program main
