! Setup adapted from the author's test/test_coulomb_schroed.f90 (MIT).
! A one-electron hydrogen Coulomb potential, in atomic units (Hartree energies).
program main
   use types, only: dp
   use schroed_dirac_solver, only: total_energy
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer, parameter :: ne = 8, p = 20, nq = 43
   real(dp) :: alpha_j(-7:6), alpha(-7:6), quadrature(nq,ne), error, exact
   real(dp), allocatable :: energies(:), wavefunctions(:,:,:)
   integer :: dofs, principal, angular, index

   alpha = 0._dp
   alpha_j = -2._dp
   call total_energy(1,100._dp,ne,100._dp,p,nq,dofs,0,0,137.0359895_dp,0, &
                     -7,alpha_j,alpha,energies,wavefunctions,quadrature)
   if (.not. all(ieee_is_finite(energies))) error stop 'Nonfinite energy'
   print '(a,i0)', 'Radial finite-element degrees of freedom: ', dofs
   print *, ' n  l        Energy (Hartree)          Exact            Absolute error'
   do principal = 1, 3
      exact = -0.5_dp/real(principal**2,dp)
      do angular = 0, principal-1
         index = (principal-1)*principal/2+angular+1
         error = abs(energies(index)-exact)
         print '(2i3,2f21.12,es15.3)', principal,angular,energies(index),exact,error
         if (error > 1.e-7_dp) error stop 'Hydrogen energy check failed'
      end do
   end do
   print *, 'PASS featom'
end program main
