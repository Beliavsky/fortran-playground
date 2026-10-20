! Example: Numerical: statistics and least-squares fitting
! Try changing y; the fitted model is y = intercept + slope*x.
program statistics_and_regression
   use, intrinsic :: iso_fortran_env, only: real64
   implicit none
   real(real64), parameter :: x(5) = [1,2,3,4,5], y(5) = [2,4,5,4,5]
   real(real64) :: mx, my, slope, intercept, sample_sd
   mx = sum(x)/size(x)
   my = sum(y)/size(y)
   sample_sd = sqrt(sum((x-mx)**2)/(size(x)-1))
   slope = dot_product(x-mx,y-my)/sum((x-mx)**2)
   intercept = my - slope*mx
   print '(a,f12.8)', 'Mean x: ', mx
   print '(a,f12.8)', 'Sample standard deviation x: ', sample_sd
   print '(a,f12.8)', 'Slope: ', slope
   print '(a,f12.8)', 'Intercept: ', intercept
end program statistics_and_regression
