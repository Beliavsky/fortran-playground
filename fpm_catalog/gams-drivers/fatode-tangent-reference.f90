! Independent MIT-licensed driver; see licenses/tangents-blocks-drivers-MIT.txt.
module tangent_fixture
   use, intrinsic :: iso_fortran_env, only: real64
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer :: rhs_calls,jacobian_calls
contains
   subroutine rhs(n,t,y,f)
      integer, intent(in) :: n
      real(real64), intent(in) :: t,y(n)
      real(real64), intent(out) :: f(n)
      if (n/=4 .or. .not.all(ieee_is_finite(y))) error stop 'invalid RHS callback state'
      rhs_calls=rhs_calls+1
      f=[-y(3)*y(1)+y(4)*y(2),-y(3)*y(2),0.0_real64,0.0_real64]
   end subroutine
   subroutine jacobian(n,t,y,jac)
      integer, intent(in) :: n
      real(real64), intent(in) :: t,y(n)
      real(real64), intent(out) :: jac(n,n)
      if (n/=4 .or. .not.all(ieee_is_finite(y))) error stop 'invalid Jacobian callback state'
      jacobian_calls=jacobian_calls+1
      jac=0
      jac(1,:)=[-y(3),y(4),-y(1),y(2)]
      jac(2,2)=-y(3); jac(2,3)=-y(2)
   end subroutine
end module

program reference_tangent_flow
   use tangent_fixture
   use erk_tlm_f90_integrator, only: integrate_tlm
   implicit none
   integer, parameter :: methods(*)=[4,6]
   real(real64), parameter :: rates(*)=[0.25_real64,2.0_real64,8.0_real64]
   real(real64), parameter :: couplings(*)=[-1.5_real64,0.0_real64,2.0_real64]
   real(real64), parameter :: durations(*)=[-1.0_real64,-0.125_real64,0.125_real64,1.0_real64,2.0_real64]
   real(real64), parameter :: initials(2,3)=reshape([1.0_real64,0.5_real64,-0.75_real64,1.25_real64, &
      0.0_real64,0.0_real64],[2,3])
   real(real64) :: y(4),tangent(4,4),reference(4),derivative(4,4),rtol(4),atol(4),rtol_tlm(4,4),atol_tlm(4,4)
   real(real64) :: t0,t1,tau,e,a,b,k,c,state_error,tangent_error,max_state,max_tangent,stats(20)
   integer :: method,rate,coupling,time,initial,origin,i,status,controls(20),work(20),runs,total_rhs,total_jac
   runs=0; total_rhs=0; total_jac=0; max_state=0; max_tangent=0
   do method=1,size(methods)
      do rate=1,size(rates)
         k=rates(rate)
         do coupling=1,size(couplings)
            c=couplings(coupling)
            do time=1,size(durations)
               tau=durations(time); e=exp(-k*tau)
               do initial=1,size(initials,2)
                  a=initials(1,initial); b=initials(2,initial)
                  reference=[e*(a+c*b*tau),e*b,k,c]
                  derivative=0
                  derivative(1,:)=[e,c*tau*e,-tau*reference(1),b*tau*e]
                  derivative(2,:)=[0.0_real64,e,-tau*reference(2),0.0_real64]
                  derivative(3,3)=1; derivative(4,4)=1
                  do origin=0,1
                     t0=0.75_real64*origin; t1=t0+tau
                     y=[a,b,k,c]; tangent=0
                     do i=1,4
                        tangent(i,i)=1
                     end do
                     atol=1e-12_real64; rtol=1e-10_real64
                     atol_tlm=1e-12_real64; rtol_tlm=1e-10_real64
                     controls=0; controls(3)=methods(method); controls(4)=10000
                     controls(5)=1; controls(12)=1
                     rhs_calls=0; jacobian_calls=0
                     call integrate_tlm(t0,t1,4,4,y,tangent,atol_tlm,rtol_tlm,atol,rtol,rhs,jacobian, &
                        icntrl_u=controls,istatus_u=work,rstatus_u=stats,ierr_u=status)
                     if (status/=1) error stop 'FATODE did not return successful status 1'
                     if (.not.all(ieee_is_finite(y)) .or. .not.all(ieee_is_finite(tangent))) &
                        error stop 'nonfinite state or tangent'
                     if (.not.ieee_is_finite(stats(1))) error stop 'nonfinite exit time'
                     if (abs(stats(1)-t1)>64*epsilon(t1)*max(1.0_real64,abs(t1))) error stop 'wrong exit time'
                     if (rhs_calls<=0 .or. jacobian_calls<=0 .or. work(4)<=0) error stop 'callbacks/steps absent'
                     state_error=maxval(abs(y-reference)/(1+abs(reference)))
                     tangent_error=maxval(abs(tangent-derivative)/(1+abs(derivative)))
                     if (state_error>2e-7_real64 .or. tangent_error>2e-7_real64) &
                        error stop 'analytic flow or flow derivative differs'
                     if (any(y(3:)/=reference(3:))) error stop 'constant parameter states changed'
                     max_state=max(max_state,state_error); max_tangent=max(max_tangent,tangent_error)
                     total_rhs=total_rhs+rhs_calls; total_jac=total_jac+jacobian_calls; runs=runs+1
                  end do
               end do
            end do
         end do
      end do
   end do
   print '(a,i0,a,i0,a,i0)', 'Tangent integrations: ',runs,'; state entries: ',4*runs,'; derivative entries: ',16*runs
   print '(a,2i12)', 'Actual RHS and analytic-Jacobian callbacks: ',total_rhs,total_jac
   print '(a,2es14.5)', 'Maximum normalized state and tangent errors: ',max_state,max_tangent
   print '(a)', 'Dopri5/Dopri853, forward/backward time, full initial-state/parameter derivatives checked.'
   print '(a)', 'PASS fatode-tangent-reference'
end program
