! Independent API consumer; MIT: licenses/lookup-fastmath-drivers-MIT.txt.
program rsqrt_reference
   use, intrinsic :: iso_fortran_env, only: dp => real64
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   use fast_rsqrt, only: frsqrt
   implicit none
   real(dp) :: x(168),expected(168),values(168),root,relative_error,residual
   integer :: k,m,n,i
   n = 0
   do k = -250,250,25
      do m = 8,15
         n = n+1
         root = scale(real(m,dp)/8,k)
         x(n) = root*root
         expected(n) = 1/root
      end do
   end do
   if (n /= 168) error stop 'reciprocal square root case count'
   values = frsqrt(x)
   if (.not. all(ieee_is_finite(values))) error stop 'nonfinite reciprocal square root'
   if (any(values <= 0)) error stop 'nonpositive reciprocal square root'
   relative_error = maxval(abs(values/expected-1))
   residual = maxval(abs((x*values)*values-1))
   if (relative_error > 2.e-3_dp) error stop 'known squared-root reference'
   if (residual > 4.e-3_dp) error stop 'reciprocal-square residual'
   do i = 1,n
      if (abs(frsqrt(x(i))/values(i)-1) > 1.e-14_dp) error stop 'scalar/array reciprocal square root'
   end do
   print '(a)', '168 exact dyadic squares: roots (m/8)*2**k, m=8..15, k=-250..250 step 25.'
   print '(a,es12.4)', 'Maximum relative error versus reciprocal of known root: ',relative_error
   print '(a,es12.4)', 'Maximum normalized residual abs(x*y*y-1): ',residual
   print '(a)', 'Finite positive results and scalar/array consistency checked.'
   print '(a)', 'PASS fastmath-rsqrt-reference'
end program rsqrt_reference
