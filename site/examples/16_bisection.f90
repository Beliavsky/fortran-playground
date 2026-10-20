! Example: Numerical: root finding by bisection
! Try changing tolerance; the initial interval must bracket a root.
program bisection
   use, intrinsic :: iso_fortran_env, only: real64
   implicit none
   real(real64), parameter :: tolerance = 1.0e-10_real64
   real(real64) :: left, right, middle
   integer :: iteration
   left = 0.0_real64
   right = 1.0_real64
   do iteration = 1, 100
      middle = (left+right)/2
      if (abs(cos(middle)-middle) < tolerance) exit
      if (cos(middle)-middle > 0) then
         left = middle
      else
         right = middle
      end if
   end do
   print '(a,f14.10)', 'Root of cos(x)-x: ', middle
   print '(a,es14.6)', 'Residual: ', abs(cos(middle)-middle)
end program bisection
