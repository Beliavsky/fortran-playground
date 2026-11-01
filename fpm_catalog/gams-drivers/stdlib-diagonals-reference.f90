! Independent MIT consumer; see licenses/pca-ordering-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64, int32, int64
   use ieee_arithmetic, only: ieee_is_finite
   use stdlib_linalg, only: diag
   implicit none
   real(real64),allocatable :: v(:),a(:,:),dense(:,:),output(:),expected(:)
   real(real64) :: value
   integer :: n,k,m,i,j,r,col,constructs,extracts
   constructs=0; extracts=0
   do n=1,12
      allocate(v(n),expected(n))
      do i=1,n
         v(i)=real(2*i-n,real64)/8
      end do
      do k=-3,3
         m=n+abs(k)
         a=diag(v,k)
         if(any(shape(a)/=[m,m])) error stop 'Offset diagonal shape'
         if(.not.all(ieee_is_finite(a))) error stop 'Nonfinite diagonal matrix'
         do j=1,m
            do i=1,m
               value=0
               if(j-i==k) value=v(min(i,j))
               if(a(i,j)/=value) error stop 'Independent diagonal initialization'
            end do
         end do
         constructs=constructs+1
         output=diag(a,k)
         if(size(output)/=n) error stop 'Diagonal round-trip length'
         if(any(output/=v)) error stop 'Embedded diagonal extraction'
         allocate(dense(m,m))
         do j=1,m
            do i=1,m
               dense(i,j)=real(3*i-2*j,real64)/8
            end do
         end do
         do i=1,n
            r=i+max(-k,0); col=i+max(k,0)
            expected(i)=real(3*r-2*col,real64)/8
         end do
         output=diag(dense,k)
         if(size(output)/=n) error stop 'Dense extraction length'
         if(any(output/=expected)) error stop 'Independent dense diagonal reference'
         if(.not.all(ieee_is_finite(output))) error stop 'Nonfinite extracted diagonal'
         extracts=extracts+2
         deallocate(dense)
      end do
      deallocate(v,expected)
   end do
   print '(a,i0,a,i0)', 'Offset diagonal construction calls=',constructs,', independent/embedded extractions=',extracts
   print '(a)', 'PASS stdlib-diagonals-reference'
end program
