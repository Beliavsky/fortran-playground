module dae_model
   use iso_fortran_env, only: real64
   implicit none
contains
   subroutine residual(t,y,yp,cj,delta,ires,rpar,ipar)
      real(real64), intent(in) :: t,y(*),yp(*),cj
      real(real64), intent(out) :: delta(*)
      integer, intent(inout) :: ires,ipar(*)
      real(real64), intent(inout) :: rpar(*)
      delta(1)=yp(1)+y(1)
      delta(2)=y(2)-y(1)**2
   end subroutine
   subroutine unused_callback()
      error stop 'Unexpected optional callback'
   end subroutine
end module
program main
   use dae_model
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
   interface
      subroutine ddaskr(res,neq,t,y,yp,tout,info,rtol,atol,idid,rwork,lrw,iwork,liw,rpar,ipar,jac,psol,rt,nrt,jroot)
         import real64
         external res,jac,psol,rt
         integer :: neq,info(*),idid,lrw,iwork(*),liw,ipar(*),nrt,jroot(*)
         real(real64) :: t,y(*),yp(*),tout,rtol(*),atol(*),rwork(*),rpar(*)
      end subroutine
   end interface
   integer :: info(20),idid,iwork(100),ipar(1),jroot(1)
   real(real64) :: t,y(2),yp(2),rtol(1),atol(1),rwork(500),rpar(1)
   info=0; iwork=0; rwork=0; ipar=0; rpar=0
   t=0; y=1; yp=[-1._real64,-2._real64]
   rtol=1e-8_real64; atol=1e-10_real64
   call ddaskr(residual,2,t,y,yp,1._real64,info,rtol,atol,idid,rwork,500,iwork,100, &
      rpar,ipar,unused_callback,unused_callback,unused_callback,0,jroot)
   if (idid<0.or..not.all(ieee_is_finite(y))) error stop 'DAE solve failed'
   if (maxval(abs(y-[exp(-1._real64),exp(-2._real64)]))>1e-6_real64) error stop
   if (abs(y(2)-y(1)**2)>1e-7_real64) error stop 'Algebraic constraint failed'
   print '(a,f8.3)', 'Time:',t
   print '(a,2f16.10)', 'Computed y:',y
   print '(a,2f16.10)', 'Analytic y:',exp(-1._real64),exp(-2._real64)
   print *, 'PASS daskr'
end program
