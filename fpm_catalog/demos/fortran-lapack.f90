program main
   use iso_fortran_env, only: real64
   use linear_algebra, only: solve
   implicit none
   real(real64) :: a(2,2), b(2), x(2)
   a = reshape([3.0_real64, 1.0_real64, 1.0_real64, 2.0_real64], [2,2])
   b = [9.0_real64, 8.0_real64]
   x = solve(a, b)
   if (maxval(abs(matmul(a,x)-b)) > 1.0e-10_real64) error stop 'incorrect solution'
   print *, 'x =', x
   print *, 'PASS fortran-lapack'
end program main
