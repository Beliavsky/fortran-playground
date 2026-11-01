! Independent MIT consumer; see licenses/factorization-rules-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64
   use ieee_arithmetic, only: ieee_is_finite
   use stdlib_linalg, only: chol
   implicit none
   real(real64),allocatable :: a(:,:),original(:,:),known(:,:),lower(:,:),upper(:,:)
   real(real64) :: scale
   integer :: n,t,i,j
   do n=2,8
      allocate(a(n,n),original(n,n),known(n,n),lower(n,n),upper(n,n))
      do t=1,8
         known=0
         do i=1,n
            known(i,i)=real(i+1,real64)/2
            do j=1,i-1
               known(i,j)=real(mod(i+3*j+t,7)-3,real64)/8
            end do
         end do
         a=matmul(known,transpose(known))
         original=a
         scale=max(1._real64,maxval(abs(a)))
         lower=chol(a,lower=.true.,other_zeroed=.true.)
         upper=chol(a,lower=.false.,other_zeroed=.true.)
         if(.not.all(ieee_is_finite(lower)).or..not.all(ieee_is_finite(upper))) error stop 'Nonfinite Cholesky'
         if(maxval(abs(lower-known))>2.e-12_real64) error stop 'Known lower factor'
         if(maxval(abs(upper-transpose(known)))>2.e-12_real64) error stop 'Known upper factor'
         if(maxval(abs(matmul(lower,transpose(lower))-original))>2.e-12_real64*scale) error stop 'Lower residual'
         if(maxval(abs(matmul(transpose(upper),upper)-original))>2.e-12_real64*scale) error stop 'Upper residual'
         if(any(a/=original)) error stop 'Cholesky input changed'
      end do
      deallocate(a,original,known,lower,upper)
   end do
   print '(a)', '56 SPD matrices, orders 2..8; 112 Cholesky factors against constructed positive-diagonal factors'
   print '(a)', 'PASS stdlib-cholesky-reference'
end program
