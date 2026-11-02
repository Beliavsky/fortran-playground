! Independent MIT consumer; see licenses/banded-products-ten-drivers-MIT.txt.
program main
   use iso_fortran_env,only:wp=>real64
   use ieee_arithmetic,only:ieee_is_finite
   use SpecialMatrices,only:Hankel,matmul,dense,sp_transpose=>transpose
   implicit none
   type(Hankel)::structured
   real(wp),allocatable::c(:),r(:),a(:,:),truth(:,:),y(:,:),v(:),u(:)
   integer::m,n,i,j

   do m=2,7
      do n=2,9
         allocate(c(m+n-1),r(n),a(m,n),truth(n,3))
         do i=1,m+n-1
            c(i)=real(modulo(11*i,17)-8,wp)/8
         end do
         do j=1,n
            r(j)=real(modulo(7*j,13)-6,wp)/4
            truth(j,:)=[real(j,wp)/n,(-1._wp)**j,real(modulo(j,3),wp)]
         end do
         do j=1,n
            do i=1,m
               a(i,j)=c(i+j-1)
            end do
         end do
         structured=Hankel(c,m,n)
         call matrix_check(dense(structured),a)
         y=matmul(structured,truth);call matrix_check(y,matmul(a,truth))
         v=matmul(structured,truth(:,2))
         do i=1,m
            call check(v(i),dot_product(a(i,:),truth(:,2)))
         end do
         call matrix_check(dense(sp_transpose(structured)),transpose(a))
         u=matmul(sp_transpose(structured),v)
         do j=1,n
            call check(u(j),dot_product(a(:,j),v))
         end do
         deallocate(c,r,a,truth,y,v,u)
      end do
   end do
   print '(a)', '48 rectangular shapes: dense, vector/matrix products and transposes checked.'
   print '(a)', 'PASS specialmatrices-hankel-rectangular-products-reference'
contains
   subroutine check(a,b)
      real(wp),intent(in)::a,b
      if(.not.ieee_is_finite(a)) error stop 'Nonfinite result'
      if(abs(a-b)>2.e-9_wp*max(1._wp,abs(b))) then
         print *, 'Actual, independent reference:',a,b
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
   function dense_determinant(a) result(value)
      real(wp),intent(in)::a(:,:)
      real(wp)::value,t(size(a,1),size(a,2)),row(size(a,2)),factor
      integer::k,p,i,n
      n=size(a,1);t=a;value=1
      do k=1,n
         p=k-1+maxloc(abs(t(k:n,k)),dim=1)
         if(abs(t(p,k))<1.e-12_wp) error stop 'Unexpected singular reference'
         if(p/=k) then
            row=t(k,:);t(k,:)=t(p,:);t(p,:)=row;value=-value
         end if
         value=value*t(k,k)
         do i=k+1,n
            factor=t(i,k)/t(k,k)
            t(i,k:n)=t(i,k:n)-factor*t(k,k:n)
         end do
      end do
   end function
end program
