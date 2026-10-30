! Adapted from the author's pm_distNorm and pm_sampleMean examples.
! SPDX-License-Identifier: MIT
program main
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   use pm_kind, only: RK => RKD
   use pm_distNorm, only: getNormRand, getNormCDF
   use pm_sampleMean, only: getMean
   implicit none
   integer, parameter :: n=10000
   integer :: i, nseed
   integer, allocatable :: seed(:)
   real(RK) :: sample(n), mean, variance, x, cdf, expected, max_error

   call random_seed(size=nseed)
   allocate(seed(nseed))
   seed=[(284651+37*i, i=1,nseed)]
   call random_seed(put=seed)
   do i=1,n
      sample(i)=getNormRand(0.0_RK,1.0_RK)
   end do
   if (.not.all(ieee_is_finite(sample))) error stop 'nonfinite sample'
   mean=getMean(sample)
   if (abs(mean-sum(sample)/n)>1.0e-12_RK) error stop 'sample mean reference'
   variance=sum((sample-mean)**2)/(n-1)
   if (abs(mean)>0.05_RK) error stop 'normal sample mean'
   if (abs(variance-1.0_RK)>0.08_RK) error stop 'normal sample variance'
   max_error=0.0_RK
   do i=-6,6
      x=real(i,RK)/2
      cdf=getNormCDF(x,0.0_RK,1.0_RK)
      expected=(1.0_RK+erf(x/sqrt(2.0_RK)))/2
      if (.not.ieee_is_finite(cdf)) error stop 'nonfinite CDF'
      max_error=max(max_error,abs(cdf-expected))
   end do
   if (max_error>1.0e-12_RK) error stop 'normal CDF reference'
   print '(a,i0)', 'Standard normal samples: ',n
   print '(a,f12.7)', 'Sample mean (expected 0): ',mean
   print '(a,f12.7)', 'Sample variance (expected 1): ',variance
   print '(a,es12.4)', 'Maximum CDF reference error: ',max_error
   print '(a)', 'PASS paramonte'
end program main
