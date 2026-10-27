program main
   use mpmodule
   implicit none
   integer, parameter :: digits=100, words=digits/mpdpw+2
   type(mp_real) :: two, root, residual, tolerance
   two = mpreal(2.0d0,words)
   root = sqrt(two)
   residual = abs(root*root-two)
   tolerance = mpreal(10.0d0,words)**(-90)
   if (residual > tolerance) error stop 'high-precision identity failed'
   print *, 'Square root of 2 to 100 decimal places:'
   call mpwrite(6,digits+10,digits,root)
   print *, 'Squared result agrees with 2 to at least 90 decimal places.'
   print *, 'PASS mpfun2020-var1'
end program main
