! Independent API consumer; see licenses/sparse-advection-drivers-MIT.txt.
module checked_periodic_operator
   use hrweno_kinds, only: rk
   use hrweno_weno, only: weno
   implicit none
   type(weno) :: reconstruction
   integer :: n
   real(rk) :: dx,speed
contains
   subroutine rhs(t,u,du)
      real(rk), intent(in) :: t,u(:)
      real(rk), intent(out) :: du(:)
      real(rk) :: extended(n+6),left(n+6),right(n+6),flux(0:n)
      integer :: j
      extended(4:n+3)=u
      extended(1:3)=u(n-2:n)
      extended(n+4:n+6)=u(1:3)
      call reconstruction%reconstruct(extended,left,right)
      do j=0,n-1
         if (speed>0) then
            flux(j)=speed*right(j+3)
         else
            flux(j)=speed*left(j+4)
         end if
      end do
      flux(n)=flux(0)
      du=-(flux(1:n)-flux(0:n-1))/dx
   end subroutine rhs
end module checked_periodic_operator

program checked_periodic_advection
   use checked_periodic_operator
   use hrweno_tvdode, only: rktvd
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer, parameter :: sizes(3)=[64,128,256]
   real(rk), parameter :: pi=acos(-1.0_rk),velocities(2)=[-1.5_rk,0.75_rk]
   real(rk), parameter :: origins(2)=[0.0_rk,0.37_rk],amplitudes(2)=[0.2_rk,-0.3_rk]
   real(rk), parameter :: means(2)=[1.25_rk,-0.5_rk]
   real(rk), allocatable :: centers(:),u(:),exact(:)
   real(rk) :: time,target,dt,amplitude,mean,origin,factor,error,bound,mass_error
   real(rk) :: worst_relative=0,worst_mass=0,worst_fraction=0
   integer :: s,k,mode,v,p,a,i,checkpoint,problems=0,entries=0
   do s=1,3
      n=sizes(s); dx=1.0_rk/n
      allocate(centers(n),u(n),exact(n))
      centers=[((real(i,rk)-0.5_rk)*dx,i=1,n)]
      do k=2,3
         reconstruction=weno(ncells=n+6,k=k,eps=1e-6_rk)
         do mode=0,2
            factor=1
            if (mode>0) factor=sin(pi*mode*dx)/(pi*mode*dx)
            do v=1,2
               speed=velocities(v); dt=0.2_rk*dx/abs(speed)
               do p=1,2
                  origin=origins(p)
                  do a=1,2
                     amplitude=amplitudes(a); mean=means(a)
                     u=mean+amplitude*factor*sin(2*pi*mode*(centers-origin))
                     block
                        type(rktvd) :: integrator
                        integrator=rktvd(rhs,n,order=3)
                        time=0
                        do checkpoint=1,2
                           target=real(checkpoint,rk)*0.0625_rk/abs(speed)
                           call integrator%integrate(u,time,target,dt)
                           if (.not.all(ieee_is_finite(u))) error stop 'nonfinite advection'
                           ! This fixed-step API returns the first time beyond tout, not an interpolated output.
                           if (.not.ieee_is_finite(time)) error stop 'nonfinite output time'
                           if (time<target.or.time>target+dt+1e-12_rk) error stop 'advection output time'
                           exact=mean+amplitude*factor*sin(2*pi*mode*(centers-origin-speed*time))
                           error=maxval(abs(u-exact))
                           bound=5e-12_rk
                           if (mode>0) bound=bound+0.002_rk*abs(amplitude)*(real(mode*64,rk)/n)**2
                           if (error>bound) then
                              print *, 'Advection diagnostic: ',n,k,mode,speed,origin,amplitude,error,bound
                              error stop 'analytic cell-average solution'
                           end if
                           mass_error=abs(sum(u)*dx-mean)/(1+abs(mean))
                           if (mass_error>5e-12_rk) error stop 'periodic mass conservation'
                           worst_relative=max(worst_relative,error/abs(amplitude))
                           worst_mass=max(worst_mass,mass_error)
                           worst_fraction=max(worst_fraction,error/bound)
                           entries=entries+n
                        end do
                     end block
                     problems=problems+1
                  end do
               end do
            end do
         end do
      end do
      deallocate(centers,u,exact)
   end do
   print '(a,i0)', 'Periodic advection problems: ',problems
   print '(a,i0)', 'Analytic cell-average references: ',entries
   print '(a,es12.4)', 'Maximum amplitude-scaled cell error: ',worst_relative
   print '(a,es12.4)', 'Maximum error / fixture bound: ',worst_fraction
   print '(a,es12.4)', 'Maximum normalized mass error: ',worst_mass
   print '(a)', 'PASS hrweno-advection-reference'
end program checked_periodic_advection
