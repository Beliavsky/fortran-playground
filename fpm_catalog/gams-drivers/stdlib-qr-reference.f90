! Independent MIT consumer; see licenses/factorization-rules-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64
   use ieee_arithmetic, only: ieee_is_finite
   use stdlib_linalg, only: qr,linalg_state_type
   implicit none
   type(linalg_state_type) :: state
   real(real64) :: a(5,3),original(5,3),q(5,3),r(3,3),fullq(5,5),fullr(5,3),eye(5,5),scale
   integer :: t,i,j
   eye=0
   do i=1,5
      eye(i,i)=1
   end do
   do t=1,64
      do j=1,3
         do i=1,5
            a(i,j)=real(mod(t+7*i+3*j,17)-8,real64)/8
            if(i==j) a(i,j)=a(i,j)+j+2
         end do
      end do
      original=a
      scale=max(1._real64,maxval(abs(a)))
      call qr(a,q,r,err=state)
      if(.not.state%ok()) error stop 'Reduced QR status'
      if(.not.all(ieee_is_finite(q)).or..not.all(ieee_is_finite(r))) error stop 'Nonfinite reduced QR'
      if(maxval(abs(matmul(q,r)-original))>5.e-12_real64*scale) error stop 'Reduced reconstruction'
      if(maxval(abs(matmul(transpose(q),q)-eye(:3,:3)))>5.e-12_real64) error stop 'Reduced orthogonality'
      do j=1,3
         if(any(abs(r(j+1:3,j))>5.e-12_real64*scale)) error stop 'Reduced triangularity'
      end do
      if(any(a/=original)) error stop 'Reduced input changed'
      call qr(a,fullq,fullr,err=state)
      if(.not.state%ok()) error stop 'Full QR status'
      if(.not.all(ieee_is_finite(fullq)).or..not.all(ieee_is_finite(fullr))) error stop 'Nonfinite full QR'
      if(maxval(abs(matmul(fullq,fullr)-original))>5.e-12_real64*scale) error stop 'Full reconstruction'
      if(maxval(abs(matmul(transpose(fullq),fullq)-eye))>5.e-12_real64) error stop 'Full orthogonality'
      do j=1,3
         if(any(abs(fullr(j+1:5,j))>5.e-12_real64*scale)) error stop 'Full triangularity'
      end do
      if(any(a/=original)) error stop 'Full input changed'
   end do
   print '(a)', '64 real 5x3 matrices; 128 full/reduced QR decompositions, reconstruction, orthogonality and triangularity'
   print '(a)', 'PASS stdlib-qr-reference'
end program
