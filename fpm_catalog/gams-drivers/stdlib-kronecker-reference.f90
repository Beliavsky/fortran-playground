! Independent MIT consumer; see licenses/pca-ordering-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64, int32, int64
   use ieee_arithmetic, only: ieee_is_finite
   use stdlib_linalg, only: kronecker_product
   implicit none
   real(real64),allocatable :: a(:,:),b(:,:),c(:,:),x(:,:),expected(:,:),y(:)
   real(real64) :: value
   integer :: ma,na,mb,nb,t,i,j,k,l,r,col,calls
   calls=0
   do ma=1,4
      do na=1,3
         do mb=1,4
            do nb=1,3
               allocate(a(ma,na),b(mb,nb),x(nb,na),expected(mb,ma))
               do j=1,na
                  do i=1,ma
                     a(i,j)=real(i-2*j,real64)/4
                  end do
                  do i=1,nb
                     x(i,j)=real(i+j,real64)/4
                  end do
               end do
               do t=-1,1
                  do j=1,nb
                     do i=1,mb
                        b(i,j)=real(t*(2*i+j),real64)/8
                     end do
                  end do
                  c=kronecker_product(a,b)
                  if(any(shape(c)/=[ma*mb,na*nb])) error stop 'Kronecker shape'
                  if(.not.all(ieee_is_finite(c))) error stop 'Nonfinite Kronecker product'
                  do col=1,na*nb
                     do r=1,ma*mb
                        value=a((r-1)/mb+1,(col-1)/nb+1)*b(mod(r-1,mb)+1,mod(col-1,nb)+1)
                        if(c(r,col)/=value) error stop 'Independent flattened Kronecker index'
                     end do
                  end do
                  expected=0
                  do j=1,ma
                     do i=1,mb
                        do l=1,na
                           do k=1,nb
                              expected(i,j)=expected(i,j)+b(i,k)*x(k,l)*a(j,l)
                           end do
                        end do
                     end do
                  end do
                  y=matmul(c,reshape(x,[nb*na]))
                  if(any(y/=reshape(expected,[mb*ma]))) error stop 'Column-major tensor vec identity'
                  calls=calls+1
               end do
               deallocate(a,b,x,expected)
            end do
         end do
      end do
   end do
   print '(a,i0)', 'Rectangular tensor products versus independent index and column-major vec identities: ',calls
   print '(a)', 'PASS stdlib-kronecker-reference'
end program
