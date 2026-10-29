program demo_fourier_diffusion
   use constants, only: real12, int12, pi
   use globe_data, only: ra
   use solver, only: SRSin, linbcg
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer, parameter :: n = 31, steps = 50
   real(real12), parameter :: h = 1.0_real12/(n + 1), dt = 0.001_real12, r = dt/h**2
   real(real12) :: matrix(n, n), position(n), temperature(n), rhs(n), expected(n)
   real(real12) :: error, residual, discrete_factor, pde_error
   integer(int12) :: iterations
   integer :: i, step

   ! u_t = u_xx on [0,1], zero endpoint temperatures, u(x,0) = sin(pi*x).
   ! Use HeatFlow's sparse solver for backward-Euler steps of this independent
   ! one-dimensional discretization, rather than its full Cattaneo application.
   matrix = 0.0_real12
   do i = 1, n
      position(i) = i*h
      matrix(i, i) = 1.0_real12 + 2.0_real12*r
      if (i > 1) matrix(i, i - 1) = -r
      if (i < n) matrix(i, i + 1) = -r
   end do
   call SRSin(matrix, 0.0_real12, ra)
   temperature = sin(pi*position)
   do step = 1, steps
      rhs = temperature
      temperature = 0.0_real12
      iterations = 0_int12
      call linbcg(rhs, temperature, 1_int12, 1.e-11_real12, 100_int12, iterations, error)
      if (any(.not. ieee_is_finite(temperature))) error stop 'nonfinite temperature'
      residual = maxval(abs(matmul(matrix, temperature) - rhs))
      if (residual > 1.e-10_real12) error stop 'linear system residual'
   end do
   discrete_factor = (1.0_real12 + 4.0_real12*r*sin(pi*h/2.0_real12)**2)**(-steps)
   expected = discrete_factor*sin(pi*position)
   if (maxval(abs(temperature - expected)) > 1.e-9_real12) error stop 'discrete diffusion solution'
   expected = exp(-pi*pi*steps*dt)*sin(pi*position)
   pde_error = maxval(abs(temperature - expected))
   if (pde_error > 0.004_real12) error stop 'continuous solution accuracy'
   print '(a, f7.3)', 'Time: ', steps*dt
   print '(a, 2f14.9)', 'Midpoint numerical / analytical: ', temperature((n + 1)/2), expected((n + 1)/2)
   print '(a, es12.3)', 'Maximum error against the continuous heat equation: ', pde_error
   print '(a, es12.3)', 'Last independent linear-system residual: ', residual
   deallocate(ra%val, ra%irow, ra%jcol)
   print '(a)', 'PASS heatflow'
end program demo_fourier_diffusion
