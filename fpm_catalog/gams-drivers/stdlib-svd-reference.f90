! Independent MIT consumer; see licenses/factorization-rules-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64
   use ieee_arithmetic, only: ieee_is_finite
   use stdlib_linalg, only: svd,linalg_state_type
   implicit none
   type(linalg_state_type) :: state
   real(real64) :: left(4,3),right(3,3),a(4,3),original(4,3),u(4,3),vt(3,3),work(4,3)
   real(real64) :: s(3),expected(3),eye(3,3),scale
   integer :: t,rank,i,j
   left(:,1)=[1._real64,1._real64,1._real64,1._real64]/2
   left(:,2)=[1._real64,-1._real64,1._real64,-1._real64]/2
   left(:,3)=[1._real64,1._real64,-1._real64,-1._real64]/2
   right=0
   right(1,1)=0.6_real64
   right(1,2)=-0.8_real64
   right(2,1)=0.8_real64
   right(2,2)=0.6_real64
   right(3,3)=1
   eye=0
   do i=1,3
      eye(i,i)=1
   end do
   do rank=1,3
      do t=1,16
         expected=[3._real64+real(t,real64)/8,2._real64+real(t,real64)/16,1._real64+real(t,real64)/32]
         expected(rank+1:3)=0
         do j=1,3
            work(:,j)=left(:,j)*expected(j)
         end do
         a=matmul(work,transpose(right))
         original=a
         scale=max(1._real64,maxval(abs(a)))
         call svd(a,s,u,vt,full_matrices=.false.,err=state)
         if(.not.state%ok()) error stop 'SVD status'
         if(.not.all(ieee_is_finite(s)).or..not.all(ieee_is_finite(u)).or. &
            .not.all(ieee_is_finite(vt))) error stop 'Nonfinite SVD'
         if(maxval(abs(s-expected))>5.e-12_real64*scale) error stop 'Constructed singular-value oracle'
         do j=1,3
            work(:,j)=u(:,j)*s(j)
            if(maxval(abs(matmul(original,vt(j,:))-s(j)*u(:,j)))>5.e-12_real64*scale) error stop 'Left SVD residual'
            if(maxval(abs(matmul(transpose(original),u(:,j))-s(j)*vt(j,:)))> &
               5.e-12_real64*scale) error stop 'Right SVD residual'
         end do
         if(maxval(abs(matmul(work,vt)-original))>5.e-12_real64*scale) error stop 'SVD reconstruction'
         if(maxval(abs(matmul(transpose(u),u)-eye))>5.e-12_real64) error stop 'Left SVD orthogonality'
         if(maxval(abs(matmul(vt,transpose(vt))-eye))>5.e-12_real64) error stop 'Right SVD orthogonality'
         if(any(a/=original)) error stop 'SVD input changed'
      end do
   end do
   print '(a)', '48 real 4x3 matrices, ranks 1..3; 144 known singular values, paired residuals and orthogonality'
   print '(a)', 'PASS stdlib-svd-reference'
end program
