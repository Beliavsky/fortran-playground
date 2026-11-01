! Independent MIT consumer; see licenses/systems-spectra-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64
   use ieee_arithmetic, only: ieee_is_finite
   use stdlib_linalg, only: solve_constrained_lstsq
   use stdlib_linalg_state, only: linalg_state_type
   implicit none
   real(real64) :: a(6,3),a0(6,3),b(6),b0(6),c(1,3),c0(1,3),d(1),d0(1),x(3)
   real(real64) :: s(3,3),si(3,3),diag(3),h(3),u(3),v(3),expected(3),gradient(3),lambda
   type(linalg_state_type) :: err
   integer :: t,i
   do t=1,96
      a0=0; s=0; si=0
      do i=1,3
         s(i,i)=1; si(i,i)=1
         diag(i)=1+real(mod(t+i,7),real64)/4
         a0(i,i)=diag(i); a0(i+3,i)=2*diag(i)
         b(i)=real(mod(t+3*i,11)-5,real64)/8
         b(i+3)=real(mod(2*t+i,13)-6,real64)/8
      end do
      s(1,2)=real(mod(t,5)-2,real64)/4
      s(2,3)=real(mod(t,7)-3,real64)/8
      si(1,2)=-s(1,2); si(2,3)=-s(2,3); si(1,3)=s(1,2)*s(2,3)
      v=[1._real64,real(mod(t,9)-4,real64)/8,-0.5_real64]
      h=5*diag**2
      u=(diag*b(:3)+2*diag*b(4:))/h
      d=real(mod(t,17)-8,real64)/8
      lambda=(dot_product(v,u)-d(1))/sum(v*v/h)
      expected=matmul(si,u-lambda*v/h)
      a=matmul(a0,s); c(1,:)=matmul(v,s)
      a0=a; b0=b; c0=c; d0=d
      call solve_constrained_lstsq(a,b,c,d,x,err=err)
      if(.not.err%ok()) error stop 'Constrained least-squares status'
      if(.not.all(ieee_is_finite(x))) error stop 'Nonfinite constrained solution'
      if(maxval(abs(x-expected))>5.e-12_real64*max(1._real64,maxval(abs(expected)))) &
         error stop 'Independent equality-constrained minimizer'
      if(abs(dot_product(c0(1,:),x)-d0(1))>5.e-12_real64) error stop 'Equality feasibility'
      gradient=matmul(transpose(a0),matmul(a0,x)-b0)+lambda*c0(1,:)
      if(maxval(abs(gradient))>5.e-12_real64*max(1._real64,maxval(abs(b0)))) error stop 'KKT stationarity'
      if(any(a/=a0).or.any(b/=b0).or.any(c/=c0).or.any(d/=d0)) error stop 'Preserved constrained inputs'
   end do
   print '(a)', '96 equality-constrained fits versus independent diagonal-Hessian/shear oracle, feasibility and stationarity'
   print '(a)', 'PASS stdlib-constrained-ls-reference'
end program
