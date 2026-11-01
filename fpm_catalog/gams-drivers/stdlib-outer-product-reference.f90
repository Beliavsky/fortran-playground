! Independent MIT consumer; see licenses/pca-ordering-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64
   use ieee_arithmetic, only: ieee_is_finite
   use stdlib_linalg, only: outer_product
   implicit none
   real(real64),allocatable :: a(:),b(:),c(:,:),x(:),y(:)
   real(real64) :: dot,expected,frobenius
   integer :: n,m,t,i,j,k,l,calls
   calls=0
   do n=1,8
      do m=1,7
         allocate(a(n),b(m),x(m))
         do t=1,4
            do i=1,n
               a(i)=real(i-3*t,real64)/8
            end do
            do j=1,m
               b(j)=real(2*j-t,real64)/4
               x(j)=(-1._real64)**j*j/8
            end do
            if(t==4) a=0
            c=outer_product(a,b)
            if(any(shape(c)/=[n,m])) error stop 'Outer-product shape'
            if(.not.all(ieee_is_finite(c))) error stop 'Nonfinite outer product'
            do j=1,m
               do i=1,n
                  if(c(i,j)/=a(i)*b(j)) error stop 'Outer-product entry reference'
               end do
            end do
            dot=0
            do j=1,m
               dot=dot+b(j)*x(j)
            end do
            y=matmul(c,x)
            do i=1,n
               expected=a(i)*dot
               if(y(i)/=expected) error stop 'Independent rank-one matrix action'
            end do
            do i=1,n-1
               do j=1,m-1
                  if(c(i,j)*c(i+1,j+1)/=c(i,j+1)*c(i+1,j)) error stop 'Zero rank-one adjacent minors'
               end do
            end do
            frobenius=sum(c*c)
            if(frobenius/=sum(a*a)*sum(b*b)) error stop 'Outer-product Frobenius identity'
            calls=calls+1
         end do
         deallocate(a,b,x)
      end do
   end do
   print '(a,i0)', 'Rectangular rank-one products: entries, independent matrix action, minors and Frobenius identity: ',calls
   print '(a)', 'PASS stdlib-outer-product-reference'
end program
