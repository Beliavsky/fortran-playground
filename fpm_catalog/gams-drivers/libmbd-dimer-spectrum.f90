! SPDX-License-Identifier: MIT
! Independent two-oscillator consumer; see licenses/dispersion-drivers-MIT.txt.
program main
   use mbd_constants, only: dp, MBD_LOG_LVL_ERROR
   use mbd_geom, only: geom_t
   use mbd_damping, only: damping_t
   use mbd_gradients, only: grad_request_t
   use mbd_utils, only: result_t
   use mbd_hamiltonian, only: get_mbd_hamiltonian_energy
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   type(geom_t) :: geom
   type(damping_t) :: damp
   type(grad_request_t) :: grad
   type(result_t) :: result
   real(dp) :: alpha(2), omega(2), direction(3), r, a, b, c, disc
   real(dp) :: expected(6), h(6,6), energy, value, error, worst, residual, orthogonal
   integer :: iw, ia, ir, idir, mode, i, j, k, n
   worst=0; residual=0; orthogonal=0; n=0
   damp%version='bare'
   do iw=1,2
      omega=[1.0_dp,1.0_dp]
      if (iw==2) omega=[0.5_dp,1.5_dp]
      do ia=1,2
         alpha=[0.5_dp,1.0_dp]*real(ia,dp)
         do ir=1,3
            r=real(ir+1,dp)
            a=omega(1)**2; b=omega(2)**2
            c=omega(1)*omega(2)*sqrt(product(alpha))/r**3
            ! The three independent 2x2 blocks have couplings c,c,-2c.
            do i=1,3
               value=c
               if (i==3) value=-2*c
               disc=sqrt((a-b)**2+4*value**2)
               expected(2*i-1)=(a+b-disc)/2
               expected(2*i)=(a+b+disc)/2
            end do
            call sort(expected)
            energy=0.5_dp*sum(sqrt(expected))-1.5_dp*sum(omega)
            do idir=1,3
               select case(idir)
               case(1)
                  direction=[0.0_dp,0.0_dp,1.0_dp]
               case(2)
                  direction=[0.6_dp,0.8_dp,0.0_dp]
               case(3)
                  direction=[1.0_dp,2.0_dp,2.0_dp]/3
               end select
               ! Independently assemble the 6x6 Hamiltonian using scalar loops.
               h=0
               do i=1,3
                  h(i,i)=a; h(i+3,i+3)=b
                  do j=1,3
                     value=-3*direction(i)*direction(j)
                     if (i==j) value=value+1
                     h(i,j+3)=c*value; h(j+3,i)=c*value
                  end do
               end do
               do mode=1,2
                  geom%coords=reshape([1.0_dp,-2.0_dp,0.5_dp, &
                     1.0_dp+r*direction(1),-2.0_dp+r*direction(2),0.5_dp+r*direction(3)],[3,2])
                  geom%get_eigs=.true.; geom%get_modes=mode==2
                  geom%log%level=MBD_LOG_LVL_ERROR
                  call geom%init()
                  result=get_mbd_hamiltonian_energy(geom,alpha,omega,damp,grad)
                  if (geom%has_exc()) then
                     print '(a)',geom%exc%msg
                     error stop 'Hamiltonian exception'
                  end if
                  if (.not.all(ieee_is_finite(result%mode_eigs))) error stop 'nonfinite eigenvalues'
                  if (.not.ieee_is_finite(result%energy)) error stop 'nonfinite energy'
                  error=maxval(abs(result%mode_eigs-expected))/max(1.0_dp,maxval(abs(expected)))
                  worst=max(worst,error)
                  if (error>1e-12_dp) error stop 'closed-form spectrum'
                  if (abs(result%energy-energy)>1e-12_dp) error stop 'zero-point energy'
                  if (mode==2) then
                     if (.not.all(ieee_is_finite(result%modes))) error stop 'nonfinite modes'
                     do i=1,6
                        do j=1,6
                           value=0
                           do k=1,6
                              value=value+h(j,k)*result%modes(k,i)
                           end do
                           value=value-result%mode_eigs(i)*result%modes(j,i)
                           residual=max(residual,abs(value))
                           value=sum(result%modes(:,i)*result%modes(:,j))
                           if (i==j) value=value-1
                           orthogonal=max(orthogonal,abs(value))
                        end do
                     end do
                  end if
                  call geom%destroy()
                  n=n+1
               end do
            end do
         end do
      end do
   end do
   if (residual>1e-12_dp .or. orthogonal>1e-12_dp) error stop 'eigenvector residual/orthogonality'
   print '(a,i0)', 'Bare two-oscillator Hamiltonian calls: ',n
   print '(a,es12.4)', 'Maximum normalized closed-form eigenvalue error: ',worst
   print '(a,es12.4)', 'Maximum scalar eigenvector residual: ',residual
   print '(a,es12.4)', 'Maximum orthogonality error: ',orthogonal
   print '(a)', 'PASS libmbd-dimer-spectrum'
contains
   subroutine sort(x)
      real(dp),intent(inout)::x(:)
      real(dp)::t
      integer::i,j
      do i=2,size(x)
         t=x(i); j=i-1
         do while(j>=1)
            if (x(j)<=t) exit
            x(j+1)=x(j); j=j-1
         end do
         x(j+1)=t
      end do
   end subroutine sort
end program main
