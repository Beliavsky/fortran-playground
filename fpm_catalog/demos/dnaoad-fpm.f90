! Dual-number setup follows the author's app/ex1.f90 (MIT).
program main
   use config_mod, only: prec
   use dualzn_mod
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   type(dualzn) :: x, y
   complex(prec) :: z, exact
   real(prec) :: err
   integer :: k, sample

   print *, 'Derivatives 0 through 5 of exp(z) + sin(z)'
   do sample = 1, 2
      z = cmplx(0.4_prec, 0.2_prec*(sample-1), kind=prec)
      x = xto_dzn(0, 5)
      x%f(0) = z
      x%f(1) = 1.0_prec
      y = exp(x) + sin(x)
      print '(a,2f9.4)', 'z (real, imaginary) = ', real(z), aimag(z)
      do k = 0, 5
         select case (mod(k,4))
         case (0)
            exact = exp(z) + sin(z)
         case (1)
            exact = exp(z) + cos(z)
         case (2)
            exact = exp(z) - sin(z)
         case (3)
            exact = exp(z) - cos(z)
         end select
         err = abs(y%f(k)-exact)
         if (.not. ieee_is_finite(err) .or. err > 2.e-12_prec) error stop 'Incorrect derivative'
         print '(i2,2f15.10,a,es10.2)', k, real(y%f(k)), aimag(y%f(k)), ' error ', err
      end do
   end do
   print *, 'PASS dnaoad-fpm'
end program main
