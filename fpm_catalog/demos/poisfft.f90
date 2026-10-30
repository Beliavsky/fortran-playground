! A periodic one-dimensional Poisson problem with an exact sine solution.
program main
   use poisfft
   implicit none
   integer, parameter :: n = 32
   real(drp), parameter :: pi_value = acos(-1.0_drp)
   real(drp) :: rhs(n), solution(n), exact(n), x, error
   integer :: i
   type(PoisFFT_Solver1D_DP) :: solver
   do i = 1, n
      x = real(i-1, drp) / real(n, drp)
      exact(i) = sin(2.0_drp*pi_value*x)
   end do
   rhs = -(2.0_drp*pi_value)**2 * exact
   solver = PoisFFT_Solver1D_DP([n], [1.0_drp], [PoisFFT_Periodic, PoisFFT_Periodic], &
      approximation=PoisFFT_Spectral, planning=PoisFFT_Estimate)
   call Execute(solver, solution, rhs)
   call Finalize(solver)
   error = maxval(abs(solution-exact))
   print '(a,i0)', 'Periodic Poisson grid points: ', n
   print '(a,es12.4)', 'Maximum error against sin(2*pi*x): ', error
   if (error > 1.0e-10_drp) error stop 'Poisson solution is inaccurate'
   print '(a)', 'PASS poisfft'
end program main
