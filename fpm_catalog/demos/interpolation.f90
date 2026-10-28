program interpolation_demo
   use iso_fortran_env, only: dp => real64
   use interpolation, only: interp1
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   real(dp) :: x(5), y(5), xi(9), linear(9), smooth(9)
   integer :: i
   x = [0,1,2,3,4]
   xi = [(i/2.0_dp,i=0,8)]
   y = 2*x+1
   linear = interp1(x,y,xi)
   if (.not. all(ieee_is_finite(linear))) error stop 'Nonfinite interpolation'
   if (maxval(abs(linear-(2*xi+1)))>1.e-12_dp) error stop 'Linear check'
   y = [0,1,1,2,3]
   smooth = interp1(x,y,xi,method='pchip')
   if (.not. all(ieee_is_finite(smooth))) error stop 'Nonfinite PCHIP'
   if (any(smooth(2:)<smooth(:8)-1.e-12_dp)) error stop 'Monotonicity check'
   if (maxval(abs(smooth(1:9:2)-y))>1.e-12_dp) error stop 'Knot check'
   print '(a)', '       x      linear       pchip'
   do i=1,9
      print '(3f12.5)', xi(i),linear(i),smooth(i)
   end do
   print *, 'PASS interpolation'
end program
