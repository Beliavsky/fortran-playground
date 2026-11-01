! Independent MIT consumer; see licenses/systems-spectra-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64
   use ieee_arithmetic, only: ieee_is_finite
   use stdlib_linalg, only: eig
   use stdlib_linalg_state, only: linalg_state_type
   implicit none
   real(real64) :: a(3,3),a0(3,3),b(3,3),b0(3,3),s(3,3),si(3,3),t(3,3),z(3,3),q(3,3)
   real(real64) :: alpha,beta,r,scale
   complex(real64) :: values(3),expected(3),right(3,3),left(3,3),residual(3)
   logical :: used(3)
   type(linalg_state_type) :: err
   integer :: k,i,j,match
   do k=1,64
      alpha=real(mod(k,11)-5,real64)/4
      beta=real(1+mod(k,7),real64)/8
      r=3+real(mod(k,5),real64)/4
      s=0; si=0; b=0; q=0
      do i=1,3
         s(i,i)=1; si(i,i)=1; b(i,i)=2._real64**(i-1); q(i,i)=1
      end do
      s(1,2)=real(mod(k,7)-3,real64)/4
      s(2,3)=real(mod(k,5)-2,real64)/4
      si(1,2)=-s(1,2); si(2,3)=-s(2,3); si(1,3)=s(1,2)*s(2,3)
      t=0
      t(1,1)=alpha; t(2,2)=alpha; t(3,3)=r
      t(1,2)=-beta; t(2,1)=beta
      a=matmul(s,matmul(t,si))
      expected=[cmplx(alpha,beta,real64),cmplx(alpha,-beta,real64),cmplx(r,0._real64,real64)]
      b=matmul(s,matmul(b,si))
      a=matmul(b,a)
      a0=a; b0=b
      call eig(a,b,values,right=right,left=left,err=err)
      if(.not.err%ok()) error stop 'Eigenproblem status'
      if(.not.all(ieee_is_finite(real(right,real64))).or..not.all(ieee_is_finite(aimag(right)))) &
         error stop 'Nonfinite right eigenvectors'
      if(.not.all(ieee_is_finite(real(left,real64))).or..not.all(ieee_is_finite(aimag(left)))) &
         error stop 'Nonfinite left eigenvectors'
      scale=max(1._real64,maxval(abs(a0)),maxval(abs(b0)))
      do j=1,3
         if(abs(sum(abs(right(:,j))**2)-1)>8.e-12_real64) error stop 'Right vector normalization'
         if(abs(sum(abs(left(:,j))**2)-1)>8.e-12_real64) error stop 'Left vector normalization'
         residual=matmul(a0,right(:,j))-values(j)*matmul(b0,right(:,j))
         if(maxval(abs(residual))>8.e-12_real64*scale) error stop 'Right eigenvector equation'
         residual=matmul(transpose(a0),left(:,j))-conjg(values(j))*matmul(transpose(b0),left(:,j))
         if(maxval(abs(residual))>8.e-12_real64*scale) error stop 'Left eigenvector equation'
      end do
      if(.not.all(ieee_is_finite(real(values,real64))).or..not.all(ieee_is_finite(aimag(values)))) &
         error stop 'Nonfinite eigenvalues'
      used=.false.
      do j=1,3
         match=0
         do i=1,3
            if(.not.used(i).and.abs(values(j)-expected(i))<8.e-12_real64) match=i
         end do
         if(match==0) error stop 'Independent analytic eigenvalue set'
         used(match)=.true.
      end do
      if(any(a/=a0).or.any(b/=b0)) error stop 'Eigenproblem input preservation'
   end do
   print '(a)', '64 nonsymmetric three-by-three problems with analytic spectra: 192 eigenvalue references'
   print '(a)', 'PASS stdlib-generalized-eig-reference'
end program
