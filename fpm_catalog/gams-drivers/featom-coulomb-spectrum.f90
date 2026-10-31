! Original I1b API driver. MIT: licenses/boundary-spectral-drivers-MIT.txt.
program main
   use types, only: dp
   use schroed_dirac_solver, only: total_energy
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer,parameter :: elements=8,degree=20,nq=43
   real(dp) :: alpha_j(-7:6),alpha(-7:6),quadrature(nq,elements),expected,error,maximum_error
   real(dp),allocatable :: energies(:),functions(:,:,:)
   integer :: charge,dofs,n,l,index,checks
   alpha=0; alpha_j=-2
   maximum_error=0; checks=0
   do charge=1,2
      ! Nonrelativistic point-Coulomb branch; energies are in Hartree atomic units.
      call total_energy(charge,100._dp,elements,100._dp,degree,nq,dofs,0,0,137.0359895_dp,0, &
         -7,alpha_j,alpha,energies,functions,quadrature)
      if(dofs<=0 .or. size(energies)<6) error stop 'Coulomb output dimensions'
      if(size(functions,3)<6) error stop 'Coulomb function dimensions'
      if(.not.all(ieee_is_finite(energies(:6)))) error stop 'nonfinite Coulomb energies'
      if(.not.all(ieee_is_finite(functions(:,:,:6)))) error stop 'nonfinite Coulomb functions'
      print '(a,i0,a,i0)', 'Nuclear charge: ',charge,'; finite-element degrees of freedom: ',dofs
      do n=1,3
         expected=-real(charge**2,dp)/(2*real(n**2,dp))
         do l=0,n-1
            index=(n-1)*n/2+l+1
            error=abs(energies(index)-expected)
            maximum_error=max(maximum_error,error)
            if(error>1.e-7_dp) error stop 'analytic Coulomb energy'
            print '(a,2i3,a,f20.12,a,es12.3)', 'n,l=',n,l,'; energy=',energies(index),'; error=',error
            checks=checks+1
         end do
      end do
   end do
   if(checks/=12) error stop 'case count'
   print '(a,es14.5)', 'Maximum absolute energy error: ',maximum_error
   print '(a)', 'Only the first six levels per charge are checked; full wavefunction accuracy is not claimed.'
   print '(a)', 'PASS featom-coulomb-spectrum'
end program
