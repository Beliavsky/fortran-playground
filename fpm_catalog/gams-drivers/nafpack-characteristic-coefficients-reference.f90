! Independent MIT consumer; see licenses/nafpack-factors-ten-drivers-MIT.txt.
program main
   use NAFPack_kinds,only:wp=>dp
   use ieee_arithmetic,only:ieee_is_finite
   use NAFPack_matrix_tools,only: &
      Faddeev_Leverrier
   implicit none
   real(wp),allocatable::a(:,:),q(:,:),diagonal(:),coefficients(:),expected(:),residual(:,:)
   real(wp)::scale,norm,value
   integer::n,i,j,k,variant
   if(storage_size(0._wp)/=64) error stop 'Expected REAL64 NAFPack kind'
   do n=2,6
      allocate(a(n,n),q(n,n),diagonal(n),coefficients(n+1),expected(n+1),residual(n,n))
      do variant=1,3
         scale=2._wp**(variant-2);norm=real(sum([(i*i,i=1,n)]),wp);q=identity(n)
         do j=1,n
            do i=1,n
               q(i,j)=q(i,j)-2*real(i*j,wp)/norm
            end do
            diagonal(j)=scale*(-1._wp)**j*(0.25_wp+real(j,wp)/8)
         end do
         a=matmul(q*spread(diagonal,1,n),transpose(q))
         call Faddeev_Leverrier(a,coefficients,check=.false.)
         expected=0;expected(1)=1
         do j=1,n
            do k=j+1,2,-1
               expected(k)=expected(k)-diagonal(j)*expected(k-1)
            end do
         end do
         do k=1,n+1
            call check(coefficients(k),expected(k))
         end do
         residual=identity(n)*coefficients(1)
         do k=2,n+1
            residual=matmul(a,residual)+identity(n)*coefficients(k)
         end do
         call matrix_check(residual,0._wp*identity(n))
         do j=1,n
            value=coefficients(1)
            do k=2,n+1
               value=value*diagonal(j)+coefficients(k)
            end do
            call check(value,0._wp)
         end do
      end do
      deallocate(a,q,diagonal,coefficients,expected,residual)
   end do
   print '(a)', '15 characteristic polynomials: coefficient products and Cayley-Hamilton checked.'
   print '(a)', 'PASS nafpack-characteristic-coefficients-reference'
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
