! Independent API consumer; MIT: licenses/roots-splines-quadrature-drivers-MIT.txt.
program quadratic_reference
   use, intrinsic :: iso_fortran_env, only: dp => real64
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   use lib_algebra, only: quadratic
   implicit none
   real(dp), parameter :: roots(*) = [-4._dp,-2._dp,-.5_dp,0._dp,.5_dp,2._dp,4._dp]
   real(dp), parameter :: scales(*) = [-8._dp,-.5_dp,.5_dp,8._dp]
   real(dp) :: a,b,c,x(2),sorted(2),expected(2),residual,max_error,max_residual
   integer :: i,j,k,l,cases
   cases = 0
   max_error = 0._dp
   max_residual = 0._dp
   do i = 1,size(roots)-1
      do j = i+1,size(roots)
         expected = [roots(i),roots(j)]
         do k = 1,size(scales)
            a = scales(k)
            b = -a*sum(expected)
            c = a*product(expected)
            call quadratic(a,b,c,x(1),x(2))
            if (.not. all(ieee_is_finite(x))) error stop 'nonfinite quadratic roots'
            sorted = [minval(x),maxval(x)]
            max_error = max(max_error,maxval(abs(sorted-expected)))
            if (maxval(abs(sorted-expected)) > 2.e-12_dp) error stop 'known distinct roots'
            do l = 1,2
               residual = abs((a*x(l)+b)*x(l)+c)/max(1._dp,abs(a*x(l)*x(l))+abs(b*x(l))+abs(c))
               max_residual = max(max_residual,residual)
               if (residual > 2.e-12_dp) error stop 'quadratic normalized residual'
            end do
            if (abs(sum(x)-sum(expected)) > 2.e-12_dp) error stop 'root sum'
            if (abs(product(x)-product(expected)) > 2.e-12_dp) error stop 'root product'
            cases = cases+1
         end do
      end do
   end do
   if (cases /= 84) error stop 'quadratic fixture count'
   print '(a)', '84 quadratics: 21 distinct dyadic root pairs and four positive/negative coefficient scales.'
   print '(a,es12.4)', 'Maximum absolute root error: ',max_error
   print '(a,es12.4)', 'Maximum normalized polynomial residual: ',max_residual
   print '(a)', 'Root order normalized by caller; sums and products checked independently.'
   print '(a)', 'PASS fortranlib-quadratic-reference'
end program quadratic_reference
