! Independent MIT consumer; see licenses/banded-products-ten-drivers-MIT.txt.
program main
   use iso_fortran_env,only:wp=>real64
   use ieee_arithmetic,only:ieee_is_finite
   use SpecialMatrices,only:Bidiagonal,solve
   implicit none
   real(wp),allocatable::d(:),e(:),a(:,:),truth(:,:),b(:,:),x(:,:),v(:)
   complex(wp),allocatable::w(:)
   integer::n,i,j,orientation,k
   character::which
   type(Bidiagonal)::structured
   do n=2,16
      allocate(d(n),e(n-1),a(n,n),truth(n,3))
      do i=1,n
         d(i)=(-1._wp)**i*(2+real(i,wp)/8)
         if(i<n) e(i)=real(modulo(3*i,7)-3,wp)/16
         truth(i,:)=[real(i,wp)/n,(-1._wp)**i,real(modulo(i,5),wp)/4]
      end do
      do orientation=1,2
         which=merge('L','U',orientation==1);a=0
         do i=1,n
            a(i,i)=d(i)
            if(i<n) then
               if(which=='L') then
                  a(i+1,i)=e(i)
               else
                  a(i,i+1)=e(i)
               end if
            end if
         end do
         structured=Bidiagonal(d,e,which)
         b=matmul(a,truth);x=solve(structured,b)
         call matrix_check(x,truth);call matrix_check(matmul(a,x),b)
         v=solve(structured,b(:,2))
         do i=1,n
            call check(v(i),truth(i,2))
         end do
         deallocate(b,x,v)
      end do
      deallocate(d,e,a,truth)
   end do
   print '(a)', '30 lower/upper bidiagonal matrices, dimensions 2..16, checked.'
   print '(a)', 'PASS specialmatrices-bidiagonal-systems-reference'
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
