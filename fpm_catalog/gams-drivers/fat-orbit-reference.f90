! Independent API consumer; see licenses/lu-orbits-drivers-MIT.txt.
program checked_orbital_elements
   use fortran_astrodynamics_toolkit, only: orbital_elements_to_rv,wp=>fat_wp
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
   real(wp), parameter :: pi=acos(-1.0_wp),eccs(5)=[0.0_wp,0.2_wp,0.7_wp,1.0_wp,1.5_wp]
   real(wp), parameter :: inclinations(5)=[0.0_wp,0.3_wp,pi/2,pi-0.4_wp,pi]
   real(wp), parameter :: anomalies(4)=[-1.2_wp,0.0_wp,0.8_wp,2.0_wp]
   real(wp), parameter :: mus(3)=[1.0_wp,398600.4418_wp,1e6_wp],ps(3)=[2.0_wp,7000.0_wp,2e5_wp]
   real(wp) :: raan,aop,mu,p,e,inc,nu,r(3),v(3),rr(3),vv(3),h(3),ev(3),normal(3)
   real(wp) :: radius,speed_scale,energy,expected_energy,error,worst_components=0,worst_invariants=0
   integer :: ie,ii,ir,ia,it,is,cases=0
   do ie=1,5
      e=eccs(ie)
      do ii=1,5
         inc=inclinations(ii)
         do ir=1,2
            ! Undefined nodes/periapses use canonical zero angles.
            if ((ii==1.or.ii==5).and.ir==2) cycle
            raan=real(ir-1,wp)*1.2_wp
            do ia=1,2
               if (ie==1.and.ia==2) cycle
               aop=real(ia-1,wp)*0.7_wp
               do it=1,4
                  nu=anomalies(it)
                  do is=1,3
                     mu=mus(is); p=ps(is); speed_scale=sqrt(mu/p)
                     if (1+e*cos(nu)<=0) error stop 'nonphysical anomaly fixture'
                     call orbital_elements_to_rv(mu,p,e,inc,raan,aop,nu,r,v)
                     if (.not.all(ieee_is_finite(r)).or..not.all(ieee_is_finite(v))) error stop 'nonfinite state'
                     radius=p/(1+e*cos(nu))
                     rr=[radius*cos(nu),radius*sin(nu),0.0_wp]
                     vv=speed_scale*[-sin(nu),e+cos(nu),0.0_wp]
                     ! Apply three separate geometric rotations, not the library rotation matrix.
                     call rotate_z(rr,aop); call rotate_x(rr,inc); call rotate_z(rr,raan)
                     call rotate_z(vv,aop); call rotate_x(vv,inc); call rotate_z(vv,raan)
                     error=max(maxval(abs(r-rr))/p,maxval(abs(v-vv))/speed_scale)
                     worst_components=max(worst_components,error)
                     if (error>5e-12_wp) error stop 'Cartesian component reference mismatch'
                     h=cross(r,v)
                     ev=cross(v,h)/mu-r/norm2(r)
                     energy=sum(v*v)/2-mu/norm2(r)
                     expected_energy=mu*(e*e-1)/(2*p)
                     normal=[sin(raan)*sin(inc),-cos(raan)*sin(inc),cos(inc)]
                     error=max(abs(norm2(r)-radius)/p, &
                        abs(sum(h*h)/(mu*p)-1), &
                        abs(norm2(ev)-e)/(1+e), &
                        abs(energy-expected_energy)/(mu/p), &
                        abs(dot_product(r,v)/norm2(r)/speed_scale-e*sin(nu)), &
                        maxval(abs(h/sqrt(mu*p)-normal)))
                     worst_invariants=max(worst_invariants,error)
                     if (error>5e-12_wp) error stop 'orbital invariant mismatch'
                     cases=cases+1
                  end do
               end do
            end do
         end do
      end do
   end do
   print '(a,i0)', 'Orbital state conversions: ',cases
   print '(a,i0)', 'Cartesian component references: ',6*cases
   print '(a,i0)', 'Scalar invariant/direction checks: ',8*cases
   print '(a,es12.4)', 'Maximum scaled component error: ',worst_components
   print '(a,es12.4)', 'Maximum scaled invariant error: ',worst_invariants
   print '(a)', 'PASS fat-orbit-reference'
contains
   subroutine rotate_z(x,angle)
      real(wp), intent(inout) :: x(3)
      real(wp), intent(in) :: angle
      real(wp) :: a,b
      a=x(1); b=x(2)
      x(1)=cos(angle)*a-sin(angle)*b
      x(2)=sin(angle)*a+cos(angle)*b
   end subroutine rotate_z
   subroutine rotate_x(x,angle)
      real(wp), intent(inout) :: x(3)
      real(wp), intent(in) :: angle
      real(wp) :: a,b
      a=x(2); b=x(3)
      x(2)=cos(angle)*a-sin(angle)*b
      x(3)=sin(angle)*a+cos(angle)*b
   end subroutine rotate_x
   function cross(a,b) result(c)
      real(wp), intent(in) :: a(3),b(3)
      real(wp) :: c(3)
      c=[a(2)*b(3)-a(3)*b(2),a(3)*b(1)-a(1)*b(3),a(1)*b(2)-a(2)*b(1)]
   end function cross
end program checked_orbital_elements
