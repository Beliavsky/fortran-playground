! Independent MIT consumer; see licenses/banded-products-ten-drivers-MIT.txt.
program main
   use iso_fortran_env,only:wp=>real64
   use ieee_arithmetic,only:ieee_is_finite
   use SpecialMatrices,only:SymTridiagonal,det
   implicit none
   real(wp),allocatable::d(:),lo(:),hi(:),a(:,:),truth(:,:),b(:,:),x(:,:),v(:),z(:),w(:),vectors(:,:)
   real(wp)::expected
   integer::n,i,j,k,mode
   type(SymTridiagonal)::structured
   do n=2,16
      allocate(d(n),lo(n-1),hi(n-1),a(n,n),truth(n,3),b(n,3))
      do i=1,n
         d(i)=3+real(modulo(i,4),wp)/8
         if(i<n) then
            lo(i)=real(modulo(i,3)+1,wp)/8
            hi(i)=-real(modulo(i,5)+1,wp)/16
         end if
      end do
      hi=lo
      a=0
      do i=1,n
         a(i,i)=d(i)
         if(i<n) then
            a(i+1,i)=lo(i);a(i,i+1)=hi(i)
         end if
         truth(i,:)=[real(i,wp)/n,(-1._wp)**i,real(modulo(3*i,7)-3,wp)/4]
      end do
      structured=SymTridiagonal(d,lo,isposdef=.true.)
      call check(det(structured),dense_determinant(a))
      deallocate(d,lo,hi,a,truth,b)
   end do
   print '(a)', '15 independently assembled matrices, dimensions 2..16, checked.'
   print '(a)', 'PASS specialmatrices-positive-tridiagonal-determinants-reference'
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
