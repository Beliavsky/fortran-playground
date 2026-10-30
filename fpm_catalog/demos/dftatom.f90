! Hydrogen check based on dftatom's MIT-licensed tests/hydrogen example.
program main
   use dftatom, only: dp, mesh_exp, mesh_exp_deriv, solve_radial_eigenproblem
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer, parameter :: points=3000, z=1
   real(dp), parameter :: rmin=1e-8_dp, rmax=80.0_dp, ratio=1e6_dp
   real(dp) :: r(points+1), rp(points+1), potential(points+1), p(points+1), q(points+1)
   real(dp) :: energy, exact, error
   integer :: n, l, status

   r = mesh_exp(rmin, rmax, ratio, points)
   rp = mesh_exp_deriv(rmin, rmax, ratio, points)
   potential = -z/r
   print '(a)', 'Hydrogen energies in Hartree: n l computed exact absolute error'
   do n=1, 3
      do l=0, n-1
         exact = -0.5_dp/n**2
         call solve_radial_eigenproblem(n, l, -0.4_dp, 1e-10_dp, 100, r, rp, potential, z, &
            137.035999037_dp, 0, .true., -1.0_dp, 0.0_dp, status, energy, p, q)
         if (status /= 0) error stop 'radial eigensolver did not converge'
         if (.not. ieee_is_finite(energy)) error stop 'nonfinite energy'
         error = abs(energy-exact)
         print '(2i3,2f16.10,es12.3)', n, l, energy, exact, error
         if (error > 1e-7_dp) error stop 'hydrogen energy mismatch'
      end do
   end do
   print *, 'PASS dftatom'
end program
