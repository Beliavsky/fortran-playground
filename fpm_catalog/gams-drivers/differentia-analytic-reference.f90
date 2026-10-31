! Independent API consumer; MIT: licenses/qr-autodiff-drivers-MIT.txt.
module callbacks
   use differentia
   implicit none
contains
   function polynomial(x) result(y)
      type(dual),intent(in)::x
      type(dual)::y
      y=x**5-3*x**3+2*x-7
   end function polynomial
   function oscillatory(x) result(y)
      type(dual),intent(in)::x
      type(dual)::y
      y=exp(x)*sin(x)+cos(2*x)
   end function oscillatory
   function positive(x) result(y)
      type(dual),intent(in)::x
      type(dual)::y
      y=log(x+3)+sqrt(x+3)+1/(x+3)
   end function positive
   function coupled(x) result(y)
      type(dual),target,intent(in)::x(:)
      type(dual)::y
      y=x(1)**2*x(2)+sin(x(3))+exp(x(1)-x(2))
   end function coupled
   subroutine vector_map(x,y)
      type(dual),target,intent(in)::x(:)
      type(dual),target,intent(out)::y(:)
      y(1)=x(1)*x(2)+sin(x(3))
      y(2)=exp(x(1))+x(2)**2-x(3)
      y(3)=x(1)/(x(3)+4)+cos(x(2))
   end subroutine vector_map
end module callbacks
program main
   use callbacks
   use ieee_arithmetic,only:ieee_is_finite
   implicit none
   real(wp)::t,z,f,df,reference,slope,x(3),g(3),eg(3),v(3),ev(3),jac(3,3),ej(3,3)
   real(wp)::bad_g(2),bad_v(2),worst,value_error,error,e
   type(JacobianWorkMemory)::work
   character(:),allocatable::err
   integer::i,which,pass,nscalar,ngrad,njac
   worst=0; value_error=0; nscalar=0; ngrad=0; njac=0
   x=[0.0_wp,0.0_wp,0.0_wp]
   call gradient(coupled,x,f,bad_g,err)
   if (.not.allocated(err)) error stop 'gradient dimension guard'
   call jacobian(vector_map,x,bad_v,jac,err=err)
   if (.not.allocated(err)) error stop 'Jacobian dimension guard'
   work=JacobianWorkMemory(3,err=err)
   if (allocated(err)) error stop 'Jacobian workspace initialization'
   do i=-16,16
      t=real(i,wp)/8
      do which=1,3
         select case(which)
         case(1)
            call derivative(polynomial,t,f,df)
            reference=t**5-3*t**3+2*t-7
            slope=5*t**4-9*t**2+2
         case(2)
            call derivative(oscillatory,t,f,df)
            reference=exp(t)*sin(t)+cos(2*t)
            slope=exp(t)*(sin(t)+cos(t))-2*sin(2*t)
         case(3)
            call derivative(positive,t,f,df)
            z=t+3
            reference=log(z)+sqrt(z)+1/z
            slope=1/z+0.5_wp/sqrt(z)-1/z**2
         end select
         call check(f,reference)
         value_error=max(value_error,error)
         call check(df,slope)
         nscalar=nscalar+1
      end do
      x=[t,real(modulo(i,7)-3,wp)/4,real(modulo(i,5)-2,wp)/3]
      e=exp(x(1)-x(2))
      reference=x(1)**2*x(2)+sin(x(3))+e
      eg=[2*x(1)*x(2)+e,x(1)**2-e,cos(x(3))]
      call gradient(coupled,x,f,g,err)
      if (allocated(err)) error stop err
      call check(f,reference)
      do which=1,3
         call check(g(which),eg(which))
      end do
      ngrad=ngrad+1
      ev=[x(1)*x(2)+sin(x(3)),exp(x(1))+x(2)**2-x(3),x(1)/(x(3)+4)+cos(x(2))]
      ej(1,:)=[x(2),x(1),cos(x(3))]
      ej(2,:)=[exp(x(1)),2*x(2),-1.0_wp]
      ej(3,:)=[1/(x(3)+4),-sin(x(2)),-x(1)/(x(3)+4)**2]
      do pass=1,2
         if (pass==1) then
            call jacobian(vector_map,x,v,jac,err=err)
         else
            call jacobian(vector_map,x,v,jac,wrk=work,err=err)
         end if
         if (allocated(err)) error stop err
         do which=1,3
            call check(v(which),ev(which))
         end do
         do which=1,3
            call check(jac(which,1),ej(which,1))
            call check(jac(which,2),ej(which,2))
            call check(jac(which,3),ej(which,3))
         end do
         njac=njac+1
      end do
   end do
   if (nscalar/=99.or.ngrad/=33.or.njac/=66) error stop 'fixture accounting'
   print '(a,3i5)', 'Scalar / gradient / Jacobian calls: ',nscalar,ngrad,njac
   print '(a)', 'Dense Jacobians checked with temporary and reused workspace; two dimension guards.'
   print '(a,es12.4)', 'Maximum normalized analytical error: ',worst
   print '(a)', 'PASS differentia-analytic-reference'
contains
   subroutine check(actual,expected)
      real(wp),intent(in)::actual,expected
      if (.not.ieee_is_finite(actual)) error stop 'nonfinite result'
      error=abs(actual-expected)/max(1.0_wp,abs(expected))
      worst=max(worst,error)
      if (error>2e-12_wp) error stop 'analytical reference'
   end subroutine check
end program main
