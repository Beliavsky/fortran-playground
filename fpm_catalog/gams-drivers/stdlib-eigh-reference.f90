! Independent MIT consumer; see licenses/factorization-rules-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64
   use ieee_arithmetic, only: ieee_is_finite
   use stdlib_linalg, only: eigh,linalg_state_type
   implicit none
   type(linalg_state_type) :: state
   real(real64),allocatable :: a(:,:),original(:,:),vectors(:,:),eye(:,:),lambda(:),expected(:),u(:)
   real(real64) :: shift,rho,scale
   integer :: n,t,i,j,triangle,checks
   checks=0
   do n=3,8
      allocate(a(n,n),original(n,n),vectors(n,n),eye(n,n),lambda(n),expected(n),u(n))
      eye=0
      do i=1,n
         eye(i,i)=1
      end do
      do t=1,8
         do i=1,n
            u(i)=mod(i+t,5)-2
         end do
         u(1)=1
         shift=-real(n,real64)/4
         rho=real(t,real64)/16
         do j=1,n
            do i=1,n
               a(i,j)=shift*eye(i,j)+rho*u(i)*u(j)
            end do
         end do
         original=a
         expected=shift
         expected(n)=shift+rho*sum(u*u)
         scale=max(1._real64,maxval(abs(a)))
         do triangle=0,1
            call eigh(a,lambda,vectors,upper_a=(triangle==1),err=state)
            if(.not.state%ok()) error stop 'Symmetric eigenproblem status'
            if(.not.all(ieee_is_finite(lambda)).or..not.all(ieee_is_finite(vectors))) error stop 'Nonfinite eigensystem'
            if(maxval(abs(lambda-expected))>3.e-12_real64*scale) error stop 'Rank-one eigenvalue oracle'
            if(maxval(abs(matmul(transpose(vectors),vectors)-eye))>3.e-12_real64) error stop 'Eigenvector orthogonality'
            do j=1,n
               if(maxval(abs(matmul(original,vectors(:,j))-lambda(j)*vectors(:,j)))> &
                  3.e-12_real64*scale) error stop 'Eigenpair residual'
            end do
            if(any(a/=original)) error stop 'Eigenproblem input changed'
            checks=checks+n
         end do
      end do
      deallocate(a,original,vectors,eye,lambda,expected,u)
   end do
   print '(a,i0)', '96 symmetric eigensystems, orders 3..8; analytic eigenvalues with repeated roots: ',checks
   print '(a)', 'PASS stdlib-eigh-reference'
end program
