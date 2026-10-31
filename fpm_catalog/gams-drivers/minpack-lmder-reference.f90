! Independent API consumer; MIT: licenses/jacobian-roots-drivers-MIT.txt.
module fit_problem
   use minpack_module,only:wp
   implicit none
   integer::family,residual_calls,jacobian_calls
   real(wp)::amplitude,exponent,rho
contains
   subroutine model(x,f,jac)
      real(wp),intent(in)::x(2)
      real(wp),intent(out)::f(5),jac(5,2)
      real(wp),parameter::noise(5)=[1.0_wp,-2.0_wp,2.0_wp,-2.0_wp,1.0_wp]
      real(wp)::t,v
      integer::i
      do i=1,5
         if (family==1) then
            t=real(i-3,wp)/2; v=exp(x(2)*t)
            f(i)=x(1)*v-amplitude*exp(exponent*t)
            jac(i,:)=[v,x(1)*t*v]
         else
            t=real(i-3,wp)
            f(i)=exp(x(1))-2+t*(x(2)**3-1)+rho*noise(i)
            jac(i,:)=[exp(x(1)),3*t*x(2)**2]
         end if
      end do
   end subroutine model
   subroutine callback(m,n,x,f,jac,ldjac,iflag)
      integer,intent(in)::m,n,ldjac
      real(wp),intent(in)::x(n)
      real(wp),intent(inout)::f(m),jac(ldjac,n)
      integer,intent(inout)::iflag
      real(wp)::values(5),derivatives(5,2)
      call model(x,values,derivatives)
      select case(iflag)
      case(1)
         f=values; residual_calls=residual_calls+1
      case(2)
         jac=derivatives; jacobian_calls=jacobian_calls+1
      end select
   end subroutine callback
end module fit_problem
program main
   use fit_problem
   use minpack_module,only:lmder1
   use ieee_arithmetic,only:ieee_is_finite
   implicit none
   real(wp),parameter::amplitudes(*)=[0.5_wp,2.0_wp],exponents(*)=[-1.0_wp,0.25_wp,1.0_wp]
   real(wp),parameter::noise_scales(*)=[-0.5_wp,-0.125_wp,0.125_wp,0.5_wp]
   real(wp)::x(2),expected(2),f(5),jac(5,2),wa(15),check_f(5),check_j(5,2),plus(5),minus(5),scratch(5,2),xp(2)
   real(wp)::step,error,worst_x,worst_j,objective,expected_objective,gradient,worst_g,value
   integer::ia,ib,start_a,start_b,noise_id,info,pivots(2),runs,exact_runs,noisy_runs,jac_entries,c
   runs=0; exact_runs=0; noisy_runs=0; jac_entries=0; worst_x=0; worst_j=0; worst_g=0
   family=1; rho=0
   do ia=1,size(amplitudes)
      amplitude=amplitudes(ia)
      do ib=1,size(exponents)
         exponent=exponents(ib); expected=[amplitude,exponent]
         do start_a=1,2
            do start_b=1,2
               x=[amplitude*real(2*start_a-1,wp)/2,exponent+real(2*start_b-3,wp)/2]
               call fit()
               exact_runs=exact_runs+1
            end do
         end do
      end do
   end do
   family=2; expected=[log(2.0_wp),1.0_wp]
   do noise_id=1,size(noise_scales)
      rho=noise_scales(noise_id)
      do start_a=1,2
         do start_b=1,2
            x=[expected(1)+real(2*start_a-3,wp)*0.7_wp,real(2*start_b-1,wp)/2]
            call fit()
            noisy_runs=noisy_runs+1
         end do
      end do
   end do
   if (runs/=40.or.exact_runs/=24.or.noisy_runs/=16.or.jac_entries/=400) error stop 'fixture accounting'
   print '(a,3i5)', 'Total / exact-fit / nonzero-residual fits: ',runs,exact_runs,noisy_runs
   print '(a,i0)', 'Analytical Jacobian entries checked by central differences at starting points: ',jac_entries
   print '(a,es12.4)', 'Maximum normalized parameter error: ',worst_x
   print '(a,es12.4)', 'Maximum normalized Jacobian finite-difference error: ',worst_j
   print '(a,es12.4)', 'Maximum absolute J-transpose-residual component: ',worst_g
   print '(a)', 'PASS minpack-lmder-reference'
contains
   subroutine fit()
      call model(x,check_f,check_j)
      do c=1,2
         step=1e-5_wp*max(1.0_wp,abs(x(c)))
         xp=x; xp(c)=xp(c)+step; call model(xp,plus,scratch)
         xp=x; xp(c)=xp(c)-step; call model(xp,minus,scratch)
         error=maxval(abs((plus-minus)/(2*step)-check_j(:,c)))/max(1.0_wp,maxval(abs(check_j(:,c))))
         if (error>2e-7_wp) error stop 'user Jacobian finite-difference check'
         worst_j=max(worst_j,error); jac_entries=jac_entries+5
      end do
      residual_calls=0; jacobian_calls=0; wa=0
      call lmder1(callback,5,2,x,f,jac,5,1e-12_wp,info,pivots,wa,size(wa))
      if (info<1.or.info>4) error stop 'MINPACK normal stopping status'
      if (residual_calls<=0.or.jacobian_calls<=0) error stop 'both callbacks required'
      if (.not.all(ieee_is_finite(x)).or..not.all(ieee_is_finite(f))) error stop 'nonfinite fit'
      call model(x,check_f,check_j)
      if (maxval(abs(check_f-f))>1e-11_wp) error stop 'returned residual consistency'
      error=maxval(abs(x-expected))/max(1.0_wp,maxval(abs(expected)))
      if (error>2e-7_wp) error stop 'known fit parameters'
      worst_x=max(worst_x,error)
      objective=sum(f*f); expected_objective=0
      if (family==2) expected_objective=14*rho**2
      if (abs(objective-expected_objective)/max(1.0_wp,expected_objective)>1e-10_wp) &
         error stop 'known minimum residual norm'
      gradient=maxval(abs([sum(check_j(:,1)*f),sum(check_j(:,2)*f)]))
      if (gradient>1e-6_wp) error stop 'least-squares stationarity'
      worst_g=max(worst_g,gradient)
      if (family==1.and.maxval(abs(f))>1e-8_wp) error stop 'exact-fit residual'
      runs=runs+1
   end subroutine fit
end program main
