! Independent API consumer; MIT: licenses/rkf-qags-drivers-MIT.txt.
module models
   use rkf45_module,only:rk
   implicit none
   integer::family,evaluations
   real(rk)::rate,frequency,start,initial(2),offset(2)
contains
   subroutine rhs(t,y,dy)
      real(rk),intent(in)::t,y(:)
      real(rk),intent(out)::dy(:)
      evaluations=evaluations+1
      select case(family)
      case(1)
         dy=[-rate*y(1)-frequency*y(2),frequency*y(1)-rate*y(2)]
      case(2)
         dy(1)=-rate*(y(1)-sin(frequency*t)-t*t)+frequency*cos(frequency*t)+2*t
         dy(2)=-rate*(y(2)-cos(frequency*t)-t)-frequency*sin(frequency*t)+1
      case(3)
         dy=[rate*y(1)*(1-y(1)),0.5_rk*rate*y(2)*(1-y(2))]
      end select
   end subroutine rhs
   function exact(t) result(y)
      real(rk),intent(in)::t
      real(rk)::y(2),elapsed,angle,factor
      elapsed=t-start
      select case(family)
      case(1)
         angle=frequency*elapsed; factor=exp(-rate*elapsed)
         y=factor*[initial(1)*cos(angle)-initial(2)*sin(angle), &
                   initial(1)*sin(angle)+initial(2)*cos(angle)]
      case(2)
         y=[sin(frequency*t)+t*t,cos(frequency*t)+t]+exp(-rate*elapsed)*offset
      case(3)
         y(1)=initial(1)/(initial(1)+(1-initial(1))*exp(-rate*elapsed))
         y(2)=initial(2)/(initial(2)+(1-initial(2))*exp(-0.5_rk*rate*elapsed))
      end select
   end function exact
end module models
program main
   use models
   use rkf45_module,only:rkf45
   use ieee_arithmetic,only:ieee_is_finite
   implicit none
   real(rk)::y(2),expected(2),t,finish,target,relative,absolute,work(15),error,worst,invariant
   integer::iwork(5),flag,rate_id,init_id,direction,i,runs,calls,total_evaluations
   if (precision(1.0_rk)<15) error stop 'double precision required'
   runs=0; calls=0; total_evaluations=0; worst=0
   do family=1,3
      do rate_id=1,2
         rate=0.25_rk
         if (rate_id==2) rate=1
         frequency=real(2*rate_id-1,rk)
         do init_id=1,2
            do direction=1,2
               start=-0.5_rk; finish=1.5_rk
               if (direction==2) then
                  start=1.5_rk; finish=-0.5_rk
               end if
               initial=[1.0_rk,-0.5_rk]; offset=[0.25_rk,-0.5_rk]
               if (init_id==2) then
                  initial=[-0.25_rk,2.0_rk]; offset=[-0.75_rk,0.125_rk]
               end if
               if (family==3) then
                  initial=[0.25_rk,0.75_rk]
                  if (init_id==2) initial=[0.1_rk,0.6_rk]
               end if
               y=exact(start); t=start; evaluations=0
               relative=1e-10_rk; absolute=1e-12_rk
               work=0; iwork=0; flag=1
               do i=1,16
                  target=start+(finish-start)*real(i,rk)/16
                  call rkf45(rhs,2,y,t,target,relative,absolute,flag,work,iwork)
                  if (flag/=2) then
                     print '(a,5i5)', 'Family/rate/start/direction/flag: ',family,rate_id,init_id,direction,flag
                     error stop 'RKF45 did not reach target normally'
                  end if
                  if (abs(t-target)>16*epsilon(t)*max(1.0_rk,abs(target))) error stop 'wrong target time'
                  if (.not.all(ieee_is_finite(y))) error stop 'nonfinite ODE state'
                  expected=exact(target)
                  error=maxval(abs(y-expected))/max(1.0_rk,maxval(abs(expected)))
                  if (error>5e-8_rk) error stop 'analytical ODE reference'
                  worst=max(worst,error)
                  if (family==1) then
                     invariant=sum(initial**2)*exp(-2*rate*(target-start))
                     if (abs(sum(y**2)-invariant)/max(1.0_rk,invariant)>1e-7_rk) &
                        error stop 'oscillator decay invariant'
                  end if
                  if (family==3) then
                     if (any(y<=0).or.any(y>=1)) error stop 'logistic invariant interval'
                  end if
                  calls=calls+1
               end do
               if (evaluations<=0) error stop 'RHS callback not used'
               total_evaluations=total_evaluations+evaluations
               runs=runs+1
            end do
         end do
      end do
      print '(a,i0,a)', 'Family ',family,': forward/backward runs at two rates and two initial states passed.'
   end do
   if (runs/=24.or.calls/=384) error stop 'fixture accounting'
   print '(a,i0,a,i0)', 'Integration runs: ',runs,'; requested target calls: ',calls
   print '(a,i0)', 'RHS evaluations: ',total_evaluations
   print '(a,es12.4)', 'Maximum normalized analytical state error: ',worst
   print '(a)', 'PASS rkf45-analytic-reference'
end program main
