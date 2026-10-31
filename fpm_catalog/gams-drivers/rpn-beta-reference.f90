! Independent API consumer; MIT: licenses/circuits-beta-drivers-MIT.txt.
program beta_reference
   use assert, only: wp
   use funcs, only: beta
   use, intrinsic :: iso_fortran_env, only: int64
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer(int64) :: factorial(0:15)
   integer :: i,j,cases
   real(wp) :: x,y,reference,pi,max_error,values(4),expected(4)
   factorial(0) = 1_int64
   do i = 1,15
      factorial(i) = i*factorial(i-1)
   end do
   pi = acos(-1._wp)
   cases = 0
   max_error = 0._wp
   do i = 1,8
      do j = 1,8
         x = real(i,wp)
         y = real(j,wp)
         reference = real(factorial(i-1),wp)*real(factorial(j-1),wp)/real(factorial(i+j-1),wp)
         call check
      end do
   end do
   do i = 0,7
      do j = 0,7
         x = real(i,wp)+.5_wp
         y = real(j,wp)+.5_wp
         reference = pi*real(factorial(2*i),wp)/real(factorial(i),wp) &
            *real(factorial(2*j),wp)/real(factorial(j),wp)/4._wp**(i+j)/real(factorial(i+j),wp)
         call check
      end do
   end do
   if (cases /= 128) error stop 'beta case count'
   print '(a)', '128 positive integer/half-integer pairs; 512 beta evaluations checked.'
   print '(a)', 'Independent factorial identities, symmetry and both one-step recurrences checked.'
   print '(a,es12.4)', 'Maximum relative error against closed-form references: ',max_error
   print '(a)', 'PASS rpn-beta-reference'
contains
   subroutine check
      values = [beta(x,y),beta(y,x),beta(x+1,y),beta(x,y+1)]
      expected = [reference,reference,x/(x+y)*reference,y/(x+y)*reference]
      if (.not. all(ieee_is_finite(values))) error stop 'nonfinite beta'
      if (any(values <= 0)) error stop 'nonpositive beta'
      max_error = max(max_error,maxval(abs(values/expected-1)))
      if (maxval(abs(values/expected-1)) > 2.e-13_wp) error stop 'independent beta reference'
      cases = cases+1
   end subroutine check
end program beta_reference
