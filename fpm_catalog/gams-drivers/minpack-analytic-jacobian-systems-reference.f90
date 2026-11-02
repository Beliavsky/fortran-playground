! Independent MIT consumer; see licenses/integrals-tensors-ten-drivers-MIT.txt.
module manufactured_system
   use minpack_module, only: wp,hybrj1
   implicit none
   integer :: function_calls=0,jacobian_calls=0
contains
   subroutine equations(n,x,f,jac,ldjac,iflag)
      integer,intent(in) :: n,ldjac
      integer,intent(inout) :: iflag
      real(wp),intent(in) :: x(n)
      real(wp),intent(inout) :: f(n),jac(ldjac,n)
      real(wp) :: u(n)
      integer :: i
      u=x-[(real(i,wp)/4,i=1,n)]
      if(iflag==1) then
         function_calls=function_calls+1
         f=u+u**3/8
         do i=2,n
            f(i)=f(i)+u(i-1)**2/4
         end do
      else if(iflag==2) then
         jacobian_calls=jacobian_calls+1; jac=0
         do i=1,n
            jac(i,i)=1+3*u(i)**2/8
            if(i>1) jac(i,i-1)=u(i-1)/2
         end do
      end if
   end subroutine
end module
program main
   use manufactured_system
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
   real(wp),allocatable :: x(:),f(:),jac(:,:),work(:),reference(:),expected(:)
   real(wp) :: maximum_error,residual
   integer :: n,k,scale,i,lwa,info,flag,cases
   cases=0; maximum_error=0; residual=0
   do n=2,6
      lwa=n*(n+13)/2
      allocate(x(n),f(n),jac(n,n),work(lwa),reference(n),expected(n))
      expected=[(real(i,wp)/4,i=1,n)]
      do k=1,3
         do scale=-2,1
            x=expected+[(real((-1)**(i+k),wp)*2._wp**scale*real(i+k,wp)/real(n+k,wp),i=1,n)]
            function_calls=0; jacobian_calls=0
            call hybrj1(equations,n,x,f,jac,n,1.e-10_wp,info,work,lwa)
            if(info/=1) error stop 'MINPACK convergence status'
            if(function_calls<=0.or.jacobian_calls<=0) error stop 'Callback paths not used'
            if(.not.all(ieee_is_finite(x)).or..not.all(ieee_is_finite(f))) error stop 'Nonfinite root/residual'
            reference=x-expected
            do i=n,2,-1
               reference(i)=reference(i)+reference(i)**3/8+(x(i-1)-expected(i-1))**2/4
            end do
            reference(1)=reference(1)+reference(1)**3/8
            if(maxval(abs(reference))>1.e-8_wp.or.maxval(abs(x-expected))>1.e-8_wp) error stop 'Known root'
            if(maxval(abs(f-reference))>1.e-12_wp) error stop 'Returned residual consistency'
            maximum_error=max(maximum_error,maxval(abs(x-expected)))
            residual=max(residual,maxval(abs(reference))); cases=cases+1
         end do
      end do
      deallocate(x,f,jac,work,reference,expected)
   end do
   print '(a,i0)', 'Known-root triangular nonlinear systems with analytic Jacobians: ',cases
   print '(a,es12.4,a,es12.4)', 'Maximum root error: ',maximum_error,'; residual: ',residual
   print '(a)', 'PASS minpack-analytic-jacobian-systems-reference'
end program
