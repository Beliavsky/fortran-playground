program main
   use fstats, only: mean, variance, normal_distribution
   use iso_fortran_env, only: real64
   implicit none
   real(real64) :: samples(5), average, sample_variance, probability
   type(normal_distribution) :: normal
   samples = [1.0_real64,2.0_real64,3.0_real64,4.0_real64,5.0_real64]
   average = mean(samples)
   sample_variance = variance(samples)
   normal%mean_value = 0.0_real64
   normal%standard_deviation = 1.0_real64
   probability = normal%cdf(0.0_real64)
   if (abs(average-3.0_real64) > 1.e-12_real64) error stop 'incorrect mean'
   if (abs(sample_variance-2.5_real64) > 1.e-12_real64) error stop 'incorrect sample variance'
   if (abs(probability-0.5_real64) > 1.e-12_real64) error stop 'incorrect normal CDF'
   print *, 'Mean and sample variance:', average, sample_variance
   print *, 'Standard normal probability P(X <= 0):', probability
   print *, 'PASS fstats'
end program main
