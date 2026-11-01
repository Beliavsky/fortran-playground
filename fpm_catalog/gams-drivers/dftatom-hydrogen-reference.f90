! Independent MIT-licensed driver; see licenses/radial-dense-drivers-MIT.txt.
program reference_coulomb_states
   use dftatom, only: dp,mesh_exp,mesh_exp_deriv,solve_radial_eigenproblem
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer, parameter :: charges(*)=[1,2,4],meshes(*)=[3000,4500]
   integer :: iz,im,z,steps,n,l,i,status,runs,entries,degree,alpha
   real(dp), allocatable :: r(:),rp(:),v(:),p(:),q(:),pref(:),qref(:)
   real(dp) :: energy,exact_energy,rho,poly,dpoly,constant,norm,mean_r,mean_inverse_r,phase
   real(dp) :: energy_error,p_error,q_error,norm_error,r_error,inverse_error
   real(dp) :: max_energy,max_p,max_q,max_norm,max_r,max_inverse
   runs=0; entries=0; max_energy=0; max_p=0; max_q=0; max_norm=0; max_r=0; max_inverse=0
   do iz=1,size(charges)
      z=charges(iz)
      do im=1,size(meshes)
         steps=meshes(im)
         allocate(r(steps+1),rp(steps+1),v(steps+1),p(steps+1),q(steps+1),pref(steps+1),qref(steps+1))
         r=mesh_exp(1e-8_dp/z,100.0_dp/z,1e6_dp,steps)
         rp=mesh_exp_deriv(1e-8_dp/z,100.0_dp/z,1e6_dp,steps)
         v=-real(z,dp)/r
         do n=1,3
            do l=0,n-1
               exact_energy=-real(z*z,dp)/(2*n*n)
               call solve_radial_eigenproblem(n,l,-0.4_dp*z*z/(n*n),1e-11_dp*z*z,100,r,rp,v,z, &
                  137.035999037_dp,0,.true.,-real(z*z,dp),0.0_dp,status,energy,p,q)
               if (status/=0) error stop 'radial solver did not converge'
               if (.not.ieee_is_finite(energy) .or. .not.all(ieee_is_finite(p)) .or. &
                   .not.all(ieee_is_finite(q))) error stop 'nonfinite radial result'
               degree=n-l-1; alpha=2*l+1
               constant=sqrt((2.0_dp*z/n)**3*factorial(degree)/(2*n*factorial(n+l)))
               do i=1,size(r)
                  rho=2.0_dp*z*r(i)/n
                  call laguerre_polynomial(degree,alpha,rho,poly,dpoly)
                  pref(i)=constant*r(i)*exp(-rho/2)*rho**l*poly
                  qref(i)=constant*exp(-rho/2)*((1-rho/2)*rho**l*poly+ &
                     rho*(real(l,dp)*rho**(l-1)*poly+rho**l*dpoly))
               end do
               ! Eigenfunction signs are arbitrary: align a single common sign for P and Q.
               phase=sign(1.0_dp,sum(p*pref)); p=phase*p; q=phase*q
               energy_error=abs(energy-exact_energy)/(z*z)
               p_error=maxval(abs(p-pref))/sqrt(real(z,dp))
               q_error=maxval(abs(q-qref))/real(z,dp)**1.5_dp
               norm=trapezoid(p*p)
               norm_error=abs(norm-1)
               mean_r=trapezoid(r*p*p)/norm
               mean_inverse_r=trapezoid(p*p/r)/norm
               r_error=abs(mean_r-(3.0_dp*n*n-l*(l+1))/(2*z))*z/(1+n*n)
               inverse_error=abs(mean_inverse_r-real(z,dp)/(n*n))/z
               print '(a,4i6,6es12.3)', 'Case Z,mesh,n,l and six errors: ',z,steps,n,l, &
                  energy_error,p_error,q_error,norm_error,r_error,inverse_error
               if (energy_error>1e-7_dp) error stop 'hydrogenic energy differs'
               if (p_error>2e-5_dp .or. q_error>5e-5_dp) error stop 'analytic radial shape differs'
               if (norm_error>2e-5_dp) error stop 'independent radial normalization differs'
               if (r_error>2e-5_dp .or. inverse_error>2e-5_dp) error stop 'analytic radial moment differs'
               max_energy=max(max_energy,energy_error); max_p=max(max_p,p_error); max_q=max(max_q,q_error)
               max_norm=max(max_norm,norm_error); max_r=max(max_r,r_error); max_inverse=max(max_inverse,inverse_error)
               runs=runs+1; entries=entries+size(r)
            end do
         end do
         deallocate(r,rp,v,p,q,pref,qref)
      end do
   end do
   print '(a,i0,a,i0)', 'Radial eigenproblems: ',runs,'; P references and Q references each: ',entries
   print '(a,6es14.5)', 'Max energy, P, Q, normalization, radius and inverse-radius errors: ', &
      max_energy,max_p,max_q,max_norm,max_r,max_inverse
   print '(a)', 'Nonrelativistic Coulomb states only; Dirac, general potentials and self-consistent DFT unverified.'
   print '(a)', 'PASS dftatom-hydrogen-reference'
contains
   real(dp) function factorial(k) result(value)
      integer, intent(in) :: k
      integer :: j
      value=1
      do j=2,k
         value=value*j
      end do
   end function
   subroutine laguerre_polynomial(k,a,x,value,slope)
      integer, intent(in) :: k,a
      real(dp), intent(in) :: x
      real(dp), intent(out) :: value,slope
      select case(k)
      case(0)
         value=1; slope=0
      case(1)
         value=a+1-x; slope=-1
      case(2)
         value=(x*x-2*(a+2)*x+(a+2)*(a+1))/2; slope=x-(a+2)
      case default
         error stop 'reference polynomial degree not covered'
      end select
   end subroutine
   real(dp) function trapezoid(values) result(integral)
      real(dp), intent(in) :: values(:)
      integer :: j
      integral=0
      do j=1,size(r)-1
         integral=integral+(r(j+1)-r(j))*(values(j)+values(j+1))/2
      end do
   end function
end program
