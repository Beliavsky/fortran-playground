! Original K1 API driver. MIT: licenses/applied-methods-drivers-MIT.txt.
program main
   use splpak_module, only: splpak_type,wp=>splpak_wp
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer,parameter :: n=24,ncf=10,nwrk=ncf*(ncf+1)+1,nodes(1)=[10]
   type(splpak_type) :: fit
   real(wp) :: x(1,n),y(n),weights(n),coef(ncf),work(nwrk),t,value,derivative,sse
   real(wp),parameter :: slopes(*)=[2._wp,-3._wp,0._wp],offsets(*)=[0._wp,1._wp,-2.25_wp]
   real(wp) :: maximum_value_error,maximum_derivative_error
   integer :: c,i,j,status,checks
   checks=0
   maximum_value_error=0
   maximum_derivative_error=0
   do c=1,3
      do i=1,12
         t=real(i-1,wp)/11
         x(1,2*i-1:2*i)=t
         y(2*i-1:2*i)=offsets(c)+slopes(c)*t
         weights(2*i-1:2*i)=1
         if(c==2) then
            y(2*i-1)=y(2*i-1)+.25_wp
            y(2*i)=y(2*i)-.25_wp
         end if
         if(c==3) weights(2*i-1:2*i)=1+real(i,wp)/10
      end do
      call fit%initialize(1,x,1,y,weights,n,[0._wp],[1._wp],nodes,1._wp,coef,ncf,work,nwrk,status)
      if(status/=0) error stop 'spline initialization'
      do j=0,20
         t=real(j,wp)/20
         value=fit%evaluate(1,[t],coef,[0._wp],[1._wp],nodes,status)
         if(status/=0 .or. .not.ieee_is_finite(value)) error stop 'spline value status'
         maximum_value_error=max(maximum_value_error,abs(value-offsets(c)-slopes(c)*t))
         derivative=fit%evaluate(1,[t],[1],coef,[0._wp],[1._wp],nodes,status)
         if(status/=0 .or. .not.ieee_is_finite(derivative)) error stop 'spline derivative status'
         maximum_derivative_error=max(maximum_derivative_error,abs(derivative-slopes(c)))
         checks=checks+2
      end do
      sse=0
      do j=1,n
         value=fit%evaluate(1,x(:,j),coef,[0._wp],[1._wp],nodes,status)
         if(status/=0 .or. .not.ieee_is_finite(value)) error stop 'training value status'
         sse=sse+(value-y(j))**2
      end do
      if(c==2) then
         ! Paired opposite noise makes the line the exact least-squares fit; SSE=24*(1/4)^2.
         if(abs(sse-1.5_wp)>1.e-8_wp) error stop 'known noisy least-squares objective'
      else
         if(sse>1.e-14_wp) error stop 'exact line training residual'
      end if
      print '(a,i0,a,f18.12)', 'Fit ',c,' training SSE: ',sse
      call fit%destroy()
   end do
   if(maximum_value_error>1.e-8_wp) error stop 'known fitted line'
   if(maximum_derivative_error>1.e-7_wp) error stop 'known fitted derivative'
   if(checks/=126) error stop 'case count'
   print '(a,2es14.5)', 'Maximum value/derivative errors: ',maximum_value_error,maximum_derivative_error
   print '(a)', 'PASS splpak-paired-noise-fit'
end program
