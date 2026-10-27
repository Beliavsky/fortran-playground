program main
   use SpecialMatrices, only: diagonal, Strang, Poisson2D, solve, trace, det, matmul
   use iso_fortran_env, only: real64
   implicit none
   type(diagonal) :: matrix
   type(Strang) :: laplacian
   type(Poisson2D) :: poisson
   real(real64), allocatable :: solution(:,:)
   real(real64) :: rhs(3,2), poisson_rhs(6,2)
   real(real64), allocatable :: product(:,:)
   real(real64), allocatable :: x(:)
   matrix = diagonal([2.0_real64,3.0_real64,4.0_real64])
   x = solve(matrix,[4.0_real64,9.0_real64,16.0_real64])
   if (maxval(abs(x-[2.0_real64,3.0_real64,4.0_real64])) > 1.e-12_real64) error stop 'incorrect solution'
   if (abs(trace(matrix)-9.0_real64) > 1.e-12_real64) error stop 'incorrect trace'
   if (abs(det(matrix)-24.0_real64) > 1.e-12_real64) error stop 'incorrect determinant'
   print *, 'Structured diagonal solve:', x
   print *, 'Trace and determinant:', trace(matrix), det(matrix)
   laplacian = Strang(3)
   rhs = reshape([1.,2.,3.,4.,5.,6.],[3,2])
   product = matmul(laplacian,rhs)
   if (maxval(abs(product-reshape([0.,0.,4.,3.,0.,7.],[3,2]))) > 1.e-12_real64) &
      error stop 'incorrect Strang matrix product'
   poisson = Poisson2D(3,2)
   poisson_rhs = reshape([1.,2.,3.,4.,5.,6.,7.,8.,9.,10.,11.,12.],[6,2])
   solution = solve(poisson,poisson_rhs)
   product = matmul(poisson,solution)
   if (maxval(abs(product-poisson_rhs)) > 1.e-11_real64) error stop 'incorrect Poisson solution'
   print *, 'PASS specialmatrices'
end program main
