! Independent API consumer; see licenses/dae-fft-drivers-MIT.txt.
module closed_form_dae
   use iso_fortran_env, only: real64
   implicit none
contains
   subroutine residual(t,y,yp,cj,delta,ires,rpar,ipar)
      real(real64), intent(in) :: t,y(*),yp(*),cj
      real(real64), intent(out) :: delta(*)
      integer, intent(inout) :: ires,ipar(*)
      real(real64), intent(inout) :: rpar(*)
      real(real64) :: tau
      tau=t-rpar(6)
      if (ipar(1)==1) then
         delta(1)=yp(1)+rpar(1)*y(1)
         delta(2)=yp(2)+rpar(2)*y(2)-rpar(3)*y(1)
         delta(3)=y(3)-y(1)-y(2)*y(2)
      else
         delta(1)=yp(1)-2*tau
         delta(2)=yp(2)-y(1)
         delta(3)=y(3)-sin(tau)-y(1)*y(2)
      end if
   end subroutine residual
   subroutine jacobian(t,y,yp,pd,cj,rpar,ipar)
      real(real64), intent(in) :: t,y(*),yp(*),cj
      real(real64), intent(out) :: pd(3,3)
      real(real64), intent(inout) :: rpar(*)
      integer, intent(inout) :: ipar(*)
      pd=0
      if (ipar(1)==1) then
         pd(1,1)=rpar(1)+cj; pd(2,1)=-rpar(3); pd(2,2)=rpar(2)+cj
         pd(3,1)=-1; pd(3,2)=-2*y(2); pd(3,3)=1
      else
         pd(1,1)=cj; pd(2,1)=-1; pd(2,2)=cj
         pd(3,1)=-y(2); pd(3,2)=-y(1); pd(3,3)=1
      end if
      ipar(2)=ipar(2)+1
   end subroutine jacobian
   subroutine exact(family,t,rpar,y,yp)
      integer, intent(in) :: family
      real(real64), intent(in) :: t,rpar(6)
      real(real64), intent(out) :: y(3),yp(3)
      real(real64) :: tau,a,b,c,aa,bb,ea,eb
      tau=t-rpar(6); a=rpar(1); b=rpar(2); c=rpar(3); aa=rpar(4); bb=rpar(5)
      if (family==1) then
         ea=exp(-a*tau); eb=exp(-b*tau)
         y(1)=aa*ea
         y(2)=bb*eb+c*aa*(ea-eb)/(b-a)
         y(3)=y(1)+y(2)*y(2)
         yp(1)=-a*aa*ea
         yp(2)=-b*bb*eb+c*aa*(-a*ea+b*eb)/(b-a)
         yp(3)=yp(1)+2*y(2)*yp(2)
      else
         y(1)=tau*tau+aa; y(2)=tau**3/3+aa*tau+bb
         y(3)=sin(tau)+y(1)*y(2)
         yp(1)=2*tau; yp(2)=tau*tau+aa
         yp(3)=cos(tau)+yp(1)*y(2)+y(1)*yp(2)
      end if
   end subroutine exact
   subroutine unused_callback()
      error stop 'unexpected root or Krylov callback'
   end subroutine unused_callback
end module closed_form_dae
program checked_daskr
   use closed_form_dae
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
   interface
      subroutine ddaskr(res,neq,t,y,yp,tout,info,rtol,atol,idid,rwork,lrw,iwork,liw,rpar,ipar,jac,psol,rt,nrt,jroot)
         import real64
         external res,jac,psol,rt
         integer :: neq,info(*),idid,lrw,iwork(*),liw,ipar(*),nrt,jroot(*)
         real(real64) :: t,y(*),yp(*),tout,rtol(*),atol(*),rwork(*),rpar(*)
      end subroutine ddaskr
   end interface
   integer :: family,parameter,initial,offset,jacmode,tolmode,direction
   integer :: trajectories=0,points=0,analytic_runs=0
   real(real64) :: worst_state=0,worst_derivative=0,worst_constraint=0,worst_residual=0
   do family=1,2
      do parameter=1,2
         do initial=1,2
            do offset=1,2
               do jacmode=0,1
                  do tolmode=0,1
                     do direction=-1,1,2
                        if (family==1.and.direction==-1) cycle ! Avoid exponentially unstable reverse stiff IVPs.
                        call fixture(family,parameter,initial,offset,jacmode,tolmode,direction)
                     end do
                  end do
               end do
            end do
         end do
      end do
   end do
   print '(a,i0)', 'DAE trajectories: ',trajectories
   print '(a,i0)', 'Requested checkpoints: ',points
   print '(a,i0)', 'Analytic state/derivative entries: ',6*points
   print '(a,i0)', 'Trajectories using user Jacobians: ',analytic_runs
   print '(a,es12.4)', 'Maximum normalized state error: ',worst_state
   print '(a,es12.4)', 'Maximum normalized derivative error: ',worst_derivative
   print '(a,es12.4)', 'Maximum normalized constraint error: ',worst_constraint
   print '(a,es12.4)', 'Maximum scaled residual: ',worst_residual
   print '(a)', 'PASS daskr-dae-reference'
contains
   subroutine fixture(family,parameter,initial,offset,jacmode,tolmode,direction)
      integer, intent(in) :: family,parameter,initial,offset,jacmode,tolmode,direction
      real(real64), parameter :: checkpoints(8)=[0.01_real64,0.02_real64,0.04_real64,0.08_real64, &
         0.16_real64,0.32_real64,0.64_real64,1.0_real64]
      integer :: info(20),idid,iwork(100),ipar(2),jroot(1),j,ires
      real(real64) :: t,tout,y(3),yp(3),ref(3),refp(3),rtol(3),atol(3),rwork(500),rpar(6)
      real(real64) :: state_error,derivative_error,constraint_error,delta(3),scaled,den(3),tau
      info=0; iwork=0; rwork=0; ipar=[family,0]; jroot=0
      rpar=[0.5_real64*parameter,20.0_real64,0.75_real64,1.0_real64,0.25_real64,-0.5_real64]
      if (parameter==2) rpar(2)=100
      if (initial==2) rpar(4:5)=[-0.5_real64,2.0_real64]
      if (family==2) then
         rpar(4)=rpar(4)*parameter; rpar(5)=rpar(5)/parameter
      end if
      if (offset==2) rpar(6)=0.75_real64
      info(5)=jacmode; info(2)=tolmode
      rtol=1e-10_real64; atol=1e-12_real64
      if (tolmode==1) then
         rtol=rtol*[1.0_real64,2.0_real64,4.0_real64]
         atol=atol*[1.0_real64,2.0_real64,4.0_real64]
      end if
      t=rpar(6)
      call exact(family,t,rpar,y,yp) ! Consistent initial states and derivatives are supplied explicitly.
      do j=1,8
         tout=rpar(6)+direction*checkpoints(j)
         call ddaskr(residual,3,t,y,yp,tout,info,rtol,atol,idid,rwork,500,iwork,100, &
            rpar,ipar,jacobian,unused_callback,unused_callback,0,jroot)
         if (idid/=2.and.idid/=3) error stop 'requested-output status not returned'
         if (.not.ieee_is_finite(t)) error stop 'nonfinite returned time'
         if (abs(t-tout)>32*epsilon(t)*max(1.0_real64,abs(tout))) error stop 'checkpoint not reached'
         if (.not.all(ieee_is_finite(y)).or..not.all(ieee_is_finite(yp))) error stop 'nonfinite DAE state'
         call exact(family,tout,rpar,ref,refp)
         state_error=maxval(abs(y-ref)/(1+abs(ref)))
         derivative_error=maxval(abs(yp-refp)/(1+abs(refp)))
         tau=t-rpar(6)
         if (family==1) then
            constraint_error=abs(y(3)-y(1)-y(2)**2)/(1+abs(y(3))+abs(y(1))+y(2)**2)
            den=[1+abs(yp(1))+abs(rpar(1)*y(1)), &
               1+abs(yp(2))+abs(rpar(2)*y(2))+abs(rpar(3)*y(1)), &
               1+abs(y(3))+abs(y(1))+y(2)**2]
         else
            constraint_error=abs(y(3)-sin(tau)-y(1)*y(2))/(1+abs(y(3))+abs(y(1)*y(2)))
            den=[1+abs(yp(1))+2*abs(tau),1+abs(yp(2))+abs(y(1)), &
               1+abs(y(3))+abs(sin(tau))+abs(y(1)*y(2))]
         end if
         ires=0
         call residual(t,y,yp,0.0_real64,delta,ires,rpar,ipar)
         scaled=maxval(abs(delta)/den)
         worst_state=max(worst_state,state_error); worst_derivative=max(worst_derivative,derivative_error)
         worst_constraint=max(worst_constraint,constraint_error); worst_residual=max(worst_residual,scaled)
         if (state_error>5e-7_real64.or.derivative_error>5e-6_real64) error stop 'closed-form mismatch'
         if (constraint_error>5e-9_real64.or.scaled>2e-6_real64) error stop 'DAE residual mismatch'
         points=points+1; info(1)=1 ! Continue with the existing BDF history.
      end do
      if (jacmode==1.and.ipar(2)<1) error stop 'user Jacobian was not invoked'
      if (jacmode==0.and.ipar(2)/=0) error stop 'unexpected user Jacobian invocation'
      analytic_runs=analytic_runs+jacmode; trajectories=trajectories+1
   end subroutine fixture
end program checked_daskr
