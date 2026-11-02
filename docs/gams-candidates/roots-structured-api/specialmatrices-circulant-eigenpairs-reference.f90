! Independent MIT consumer; see licenses/roots-structured-ten-drivers-MIT.txt.
program main
   use iso_fortran_env,only:wp=>real64
   use ieee_arithmetic,only:ieee_is_finite
   use SpecialMatrices,only:Circulant,eig,eigvals
   implicit none
   real(wp),allocatable::c(:),a(:,:)
   complex(wp),allocatable::w(:),v(:,:),z(:)
   complex(wp)::expected,residual
   real(wp)::pi,theta
   integer::n,i,j,k
   pi=acos(-1._wp)
   do n=3,17
      allocate(c(n),a(n,n))
      do i=1,n
         c(i)=real(modulo(3*i,7)-3,wp)/16
      end do
      c(1)=4+sum(abs(c))
      do j=1,n
         do i=1,n
            a(i,j)=c(modulo(i-j,n)+1)
         end do
      end do
      call eig(Circulant(c),w,right=v);z=eigvals(Circulant(c))
      do j=1,n
         expected=cmplx(0._wp,0._wp,wp)
         do k=1,n
            theta=-2*pi*(j-1)*(k-1)/n
            expected=expected+c(k)*cmplx(cos(theta),sin(theta),wp)
         end do
         call check(abs(w(j)-expected),0._wp);call check(abs(z(j)-expected),0._wp)
         do i=1,n
            residual=sum(a(i,:)*v(:,j))-w(j)*v(i,j)
            call check(abs(residual),0._wp)
            call check(abs(dot_product(v(:,i),v(:,j))-merge(1._wp,0._wp,i==j)),0._wp)
         end do
      end do
      deallocate(c,a,w,v,z)
   end do
   print '(a)', '15 nonsymmetric real circulants, dimensions 3..17, independently checked.' 
   print '(a)', 'PASS specialmatrices-circulant-eigenpairs-reference'
contains
   subroutine check(a,b)
      real(wp),intent(in)::a,b
      if(.not.ieee_is_finite(a)) error stop 'Nonfinite result'
      if(abs(a-b)>2.e-9_wp*max(1._wp,abs(b))) then
         print *, 'actual, reference:',a,b
         error stop 'Independent reference'
      end if
   end subroutine
end program
