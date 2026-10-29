program main
   use iso_fortran_env, only: real64
   use mpmodule
   use playground_kronrod, only: init, kronrod, nwds2
   implicit none
   integer, parameter :: n = 3
   type(mp_real) :: nodes(n+1), weights(n+1), gauss(n+1), tolerance, integral, expected
   real(real64) :: result
   integer :: power, i
   if (mpipl < 1000) error stop 'Kronrod requires MPFUN configured for at least 1000 digits'
   call init()
   tolerance = mpreal(10.0_real64, nwds2)**(-40)
   call kronrod(n, tolerance, nodes, weights, gauss)
   ! The routine returns only the nonnegative half of the symmetric 7-point rule.
   do power = 0, 10, 2
      integral = mpreal(0.0_real64, nwds2)
      do i = 1, n
         integral = integral+2*weights(i)*nodes(i)**power
      end do
      if (power == 0) integral = integral+weights(n+1)
      expected = mpreal(2.0_real64, nwds2)/(power+1)
      if (abs(integral-expected) > tolerance) error stop 'polynomial integral'
      result = dble(integral)
      print '(a,i0,a,f18.14)', 'Integral of x^', power, ' on [-1,1]: ', result
   end do
   print *, 'PASS kronrod'
end program
