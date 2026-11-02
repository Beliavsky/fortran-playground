! Independent MIT consumer; see licenses/nafpack-factors-ten-drivers-MIT.txt.
program main
   use NAFPack_kinds,only:wp=>dp
   use ieee_arithmetic,only:ieee_is_finite
   use NAFPack_matrix_decomposition,only: &
      LU_decomposition,forward,backward
   implicit none
   real(wp),allocatable::a(:,:),lower(:,:),upper(:,:),diagonal(:,:),l(:,:),u(:,:),d(:,:),q(:,:),r(:,:)
   real(wp),allocatable::truth(:),b(:),x(:),y(:)
   real(wp)::scale
   integer::n,i,j,k,variant
   if(storage_size(0._wp)/=64) error stop 'Expected REAL64 NAFPack kind'
   do n=2,10
      allocate(a(n,n),lower(n,n),upper(n,n),diagonal(n,n),l(n,n),u(n,n),d(n,n),q(n,n),r(n,n))
      allocate(truth(n),b(n),x(n),y(n))
      do variant=1,3
         scale=2._wp**(variant-2)
         lower=identity(n);upper=0;diagonal=0
         do i=1,n
            upper(i,i)=scale*(2+real(i,wp)/4)
            diagonal(i,i)=upper(i,i)
            truth(i)=real(modulo(3*i,7)-3,wp)/4
            do j=1,i-1
               lower(i,j)=real(modulo(2*i+j,5)-2,wp)/16
               upper(j,i)=scale*real(modulo(i+3*j,7)-3,wp)/16
            end do
         end do
         a=matmul(lower,upper)
         call LU_decomposition(a,l,u)
         call matrix_check(l,lower);call matrix_check(u,upper);call matrix_check(matmul(l,u),a)
         b=matmul(a,truth);y=forward(l,b);x=backward(u,y)
         do i=1,n
            call check(x(i),truth(i))
         end do
      end do
      deallocate(a,lower,upper,diagonal,l,u,d,q,r,truth,b,x,y)
   end do
   print '(a)', '27 known matrix families, dimensions 2..10 and three scales, checked.'
   print '(a)', 'PASS nafpack-known-lu-factors-reference'
contains
   subroutine check(actual,expected)
      real(wp),intent(in)::actual,expected
      if(.not.ieee_is_finite(actual)) error stop 'Nonfinite result'
      if(abs(actual-expected)>2.e-9_wp*max(1._wp,abs(expected))) then
         print *, 'Actual, expected:',actual,expected
         error stop 'Independent reference'
      end if
   end subroutine
   subroutine matrix_check(a,b)
      real(wp),intent(in)::a(:,:),b(:,:)
      integer::i,j
      if(any(shape(a)/=shape(b))) error stop 'Matrix shape'
      do j=1,size(a,2)
         do i=1,size(a,1)
            call check(a(i,j),b(i,j))
         end do
      end do
   end subroutine
   function identity(n) result(a)
      integer,intent(in)::n
      real(wp)::a(n,n)
      integer::i
      a=0
      do i=1,n
         a(i,i)=1
      end do
   end function
   function local_backward(a,b) result(x)
      real(wp),intent(in)::a(:,:),b(:)
      real(wp)::x(size(b))
      integer::i,n
      n=size(b)
      do i=n,1,-1
         x(i)=(b(i)-dot_product(a(i,i+1:n),x(i+1:n)))/a(i,i)
      end do
   end function
end program
