! Independent API consumer; MIT: licenses/jacobian-roots-drivers-MIT.txt.
module root_problem
   use forsolver,only:rk
   implicit none
   integer::family,f_calls,df_calls,complex_calls
   real(rk)::center,scale
contains
   function f(x) result(y)
      real(rk),intent(in)::x
      real(rk)::y,u
      u=x-center; f_calls=f_calls+1
      select case(family)
      case(1)
         y=scale*(u+u**3)
      case(2)
         y=scale*(exp(u)-1)
      case(3)
         y=scale*(u+0.25_rk*sin(u))
      end select
   end function f
   function df(x) result(y)
      real(rk),intent(in)::x
      real(rk)::y,u
      u=x-center; df_calls=df_calls+1
      select case(family)
      case(1)
         y=scale*(1+3*u*u)
      case(2)
         y=scale*exp(u)
      case(3)
         y=scale*(1+0.25_rk*cos(u))
      end select
   end function df
   function fc(x) result(y)
      complex(rk),intent(in)::x
      complex(rk)::y,u
      u=x-center; complex_calls=complex_calls+1
      select case(family)
      case(1)
         y=scale*(u+u**3)
      case(2)
         y=scale*(exp(u)-1)
      case(3)
         y=scale*(u+0.25_rk*sin(u))
      end select
   end function fc
end module root_problem
program main
   use root_problem
   use forsolver,only:nlsolver
   use ieee_arithmetic,only:ieee_is_finite
   implicit none
   real(rk),parameter::centers(*)=[-2.0_rk,0.0_rk,0.5_rk,3.0_rk],scales(*)=[0.5_rk,2.0_rk]
   real(rk),parameter::starts(*)=[-2.0_rk,-0.5_rk,0.5_rk,2.0_rk]
   type(nlsolver)::solver
   real(rk)::roots(3),x0,error,residual,worst_x,worst_f,spread,worst_spread
   complex(rk)::z
   integer::ic,is,istart,method,calls,cases
   calls=0; cases=0; worst_x=0; worst_f=0; worst_spread=0
   do family=1,3
      do ic=1,size(centers)
         center=centers(ic)
         do is=1,size(scales)
            scale=scales(is)
            do istart=1,size(starts)
               x0=center+starts(istart)
               do method=1,3
                  f_calls=0; df_calls=0; complex_calls=0
                  select case(method)
                  case(1)
                     call solver%set_options(nl_method='newton',maxit=100,TolFun=1e-12_rk,verbosity=0)
                     call solver%solve(F=f,dFdx=df,x0=x0,x_sol=roots(method))
                     if (f_calls<=0.or.df_calls<=0) error stop 'analytic Newton callbacks'
                  case(2)
                     call solver%set_options(nl_method='newton-quasi-fd',fdm_method='central', &
                        fdm_tol=1e-6_rk,maxit=100,TolFun=1e-12_rk,verbosity=0)
                     call solver%solve(F=f,x0=x0,x_sol=roots(method))
                     if (f_calls<=0) error stop 'finite-difference callbacks'
                  case(3)
                     call solver%set_options(nl_method='newton-quasi-cs',cs_tol=1e-20_rk, &
                        maxit=100,TolFun=1e-12_rk,verbosity=0)
                     call solver%solve(F=fc,x0=cmplx(x0,0.0_rk,rk),x_sol=z)
                     if (complex_calls<=0) error stop 'complex-step callbacks'
                     if (.not.ieee_is_finite(real(z,rk)).or..not.ieee_is_finite(aimag(z))) &
                        error stop 'nonfinite complex root'
                     if (abs(aimag(z))>1e-12_rk) error stop 'unexpected imaginary root'
                     roots(method)=real(z,rk)
                  end select
                  if (.not.ieee_is_finite(roots(method))) error stop 'nonfinite real root'
                  error=abs(roots(method)-center)/max(1.0_rk,abs(center))
                  residual=abs(f(roots(method)))/max(1.0_rk,abs(scale))
                  if (error>1e-9_rk.or.residual>1e-10_rk) error stop 'known root/residual'
                  worst_x=max(worst_x,error); worst_f=max(worst_f,residual)
                  calls=calls+1
               end do
               spread=(maxval(roots)-minval(roots))/max(1.0_rk,abs(center))
               if (spread>1e-9_rk) error stop 'Newton method disagreement'
               worst_spread=max(worst_spread,spread); cases=cases+1
            end do
         end do
      end do
   end do
   if (cases/=96.or.calls/=288) error stop 'fixture accounting'
   print '(a,i0,a,i0)', 'Unique-root fixtures: ',cases,'; three-method solves: ',calls
   print '(a)', 'Analytic Newton, central finite differences and complex step; all roots independently prescribed.'
   print '(a,es12.4)', 'Maximum normalized root error: ',worst_x
   print '(a,es12.4)', 'Maximum normalized residual: ',worst_f
   print '(a,es12.4)', 'Maximum normalized inter-method spread: ',worst_spread
   print '(a)', 'PASS forsolver-newton-reference'
end program main
