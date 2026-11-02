! Independent MIT consumer; see licenses/ordering-runge-ten-drivers-MIT.txt.
module exact_ivp
   use rklib_module,only:rk_class,wp=>rk_module_rk
   implicit none
   integer::calls=0
contains
   subroutine equation(me,t,y,dy)
      class(rk_class),intent(inout)::me
      real(wp),intent(in)::t,y(:)
      real(wp),intent(out)::dy(:)
      calls=calls+1
      dy=[-y(1),y(3),-y(2),y(4)*(1-y(4)),2*t]
   end subroutine
   function exact(t) result(y)
      real(wp),intent(in)::t
      real(wp)::y(5)
      y=[exp(-t),cos(t),-sin(t),1/(1+exp(-t)),t*t+0.25_wp]
   end function
end module
program main
   use exact_ivp
   use rklib_module,only:rk3_class
   use ieee_arithmetic,only:ieee_is_finite
   implicit none
   type(rk3_class)::solver
   integer,parameter::order=3
   real(wp)::h,t,target,y(5),next_y(5),errors(3),ratio,err,maxerr
   integer::level,checkpoint,status
   call solver%initialize(n=5,f=equation)
   do level=1,3
      h=0.1_wp/2**(level-1);t=0;y=exact(t);maxerr=0;calls=0
      do checkpoint=1,10
         target=real(checkpoint,wp)/5
         call solver%integrate(t,y,h,target,next_y)
         call solver%status(istatus=status)
         if(status/=0) error stop 'Integrator status'
         if(.not.all(ieee_is_finite(next_y))) error stop 'Nonfinite state'
         err=maxval(abs(next_y-exact(target)))
         if(err>2*h**order) error stop 'Exact solution mismatch'
         if(next_y(1)<=0.or.next_y(4)<=0.or.next_y(4)>=1) error stop 'State bounds'
         if(abs(next_y(5)-(target*target+0.25_wp))>1.e-11_wp) error stop 'Time-dependent forcing'
         maxerr=max(maxerr,err);y=next_y;t=target
      end do
      if(calls<=0) error stop 'No callback evaluations'
      errors(level)=maxerr
      print '(a,f7.4,a,es12.4,a,i0)', 'Step ',h,': maximum state error ',maxerr,', RHS calls ',calls
   end do
   do level=1,2
      if(errors(level+1)<=0) error stop 'Unresolved convergence error'
      ratio=errors(level)/errors(level+1)
      print '(a,f12.5)', 'Step-halving error ratio: ',ratio
      if(ratio<0.7_wp*2**order.or.ratio>1.4_wp*2**order) error stop 'Observed convergence order'
   end do
   print '(a)', 'Decay, oscillator, nonlinear logistic and nonautonomous polynomial states checked.'
   print '(a)', 'PASS rklib-rk3-exact-ivp-reference'
end program
