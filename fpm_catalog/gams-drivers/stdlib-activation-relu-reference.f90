! Independent MIT consumer; see licenses/activations-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64
   use ieee_arithmetic, only: ieee_is_finite
   use stdlib_specialfunctions, only: relu, relu_grad
   implicit none
   real(real64),parameter :: reference(97,1)=reshape([ &
      0.0_real64, 0.0_real64, &
      0.0_real64, 0.0_real64, &
      0.0_real64, 0.0_real64, &
      0.0_real64, 0.0_real64, &
      0.0_real64, 0.0_real64, &
      0.0_real64, 0.0_real64, &
      0.0_real64, 0.0_real64, &
      0.0_real64, 0.0_real64, &
      0.0_real64, 0.0_real64, &
      0.0_real64, 0.0_real64, &
      0.0_real64, 0.0_real64, &
      0.0_real64, 0.0_real64, &
      0.0_real64, 0.0_real64, &
      0.0_real64, 0.0_real64, &
      0.0_real64, 0.0_real64, &
      0.0_real64, 0.0_real64, &
      0.0_real64, 0.0_real64, &
      0.0_real64, 0.0_real64, &
      0.0_real64, 0.0_real64, &
      0.0_real64, 0.0_real64, &
      0.0_real64, 0.0_real64, &
      0.0_real64, 0.0_real64, &
      0.0_real64, 0.0_real64, &
      0.0_real64, 0.0_real64, &
      0.0_real64, 0.125_real64, &
      0.25_real64, 0.375_real64, &
      0.5_real64, 0.625_real64, &
      0.75_real64, 0.875_real64, &
      1.0_real64, 1.125_real64, &
      1.25_real64, 1.375_real64, &
      1.5_real64, 1.625_real64, &
      1.75_real64, 1.875_real64, &
      2.0_real64, 2.125_real64, &
      2.25_real64, 2.375_real64, &
      2.5_real64, 2.625_real64, &
      2.75_real64, 2.875_real64, &
      3.0_real64, 3.125_real64, &
      3.25_real64, 3.375_real64, &
      3.5_real64, 3.625_real64, &
      3.75_real64, 3.875_real64, &
      4.0_real64, 4.125_real64, &
      4.25_real64, 4.375_real64, &
      4.5_real64, 4.625_real64, &
      4.75_real64, 4.875_real64, &
      5.0_real64, 5.125_real64, &
      5.25_real64, 5.375_real64, &
      5.5_real64, 5.625_real64, &
      5.75_real64, 5.875_real64, &
      6.0_real64 ],[97,1])
   real(real64),parameter :: gradient_reference(97,1)=reshape([ &
      0.0_real64, 0.0_real64, &
      0.0_real64, 0.0_real64, &
      0.0_real64, 0.0_real64, &
      0.0_real64, 0.0_real64, &
      0.0_real64, 0.0_real64, &
      0.0_real64, 0.0_real64, &
      0.0_real64, 0.0_real64, &
      0.0_real64, 0.0_real64, &
      0.0_real64, 0.0_real64, &
      0.0_real64, 0.0_real64, &
      0.0_real64, 0.0_real64, &
      0.0_real64, 0.0_real64, &
      0.0_real64, 0.0_real64, &
      0.0_real64, 0.0_real64, &
      0.0_real64, 0.0_real64, &
      0.0_real64, 0.0_real64, &
      0.0_real64, 0.0_real64, &
      0.0_real64, 0.0_real64, &
      0.0_real64, 0.0_real64, &
      0.0_real64, 0.0_real64, &
      0.0_real64, 0.0_real64, &
      0.0_real64, 0.0_real64, &
      0.0_real64, 0.0_real64, &
      0.0_real64, 0.0_real64, &
      0.0_real64, 1.0_real64, &
      1.0_real64, 1.0_real64, &
      1.0_real64, 1.0_real64, &
      1.0_real64, 1.0_real64, &
      1.0_real64, 1.0_real64, &
      1.0_real64, 1.0_real64, &
      1.0_real64, 1.0_real64, &
      1.0_real64, 1.0_real64, &
      1.0_real64, 1.0_real64, &
      1.0_real64, 1.0_real64, &
      1.0_real64, 1.0_real64, &
      1.0_real64, 1.0_real64, &
      1.0_real64, 1.0_real64, &
      1.0_real64, 1.0_real64, &
      1.0_real64, 1.0_real64, &
      1.0_real64, 1.0_real64, &
      1.0_real64, 1.0_real64, &
      1.0_real64, 1.0_real64, &
      1.0_real64, 1.0_real64, &
      1.0_real64, 1.0_real64, &
      1.0_real64, 1.0_real64, &
      1.0_real64, 1.0_real64, &
      1.0_real64, 1.0_real64, &
      1.0_real64, 1.0_real64, &
      1.0_real64 ],[97,1])
   real(real64) :: x(97),saved(97),values(97),derivatives(97),expected
   integer :: i,j,checks,gradient_checks
   checks=0; gradient_checks=0
   do i=1,97
      x(i)=real(i-49,real64)/8
   end do
   saved=x
   do j=1,1
      values=relu(x)
      derivatives=relu_grad(x)
      if(.not.all(ieee_is_finite(values)).or..not.all(ieee_is_finite(derivatives))) &
         error stop 'Nonfinite activation value/derivative'
      if(any(x/=saved)) error stop 'Activation input preservation'
      do i=1,97
         expected=reference(i,j)
         if(abs(values(i)-expected)>2.e-12_real64*max(1._real64,abs(expected))) &
            error stop 'Independent high-precision activation value'
         checks=checks+1
         if(i==49) cycle ! No unique derivative required at a possible kink.
         expected=gradient_reference(i,j)
         if(abs(derivatives(i)-expected)>2.e-12_real64*max(1._real64,abs(expected))) then
            print *, 'x, actual derivative, independent derivative: ',x(i),derivatives(i),expected
            error stop 'Independent differentiated activation reference'
         end if
         gradient_checks=gradient_checks+1
      end do
   end do
   print '(a,i0,a,i0)', 'Independent 80/120-digit activation references: values=',checks,', derivatives=',gradient_checks
   print '(a)', 'PASS stdlib-activation-relu-reference'
end program
