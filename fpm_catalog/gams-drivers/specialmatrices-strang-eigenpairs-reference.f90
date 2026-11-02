! Independent MIT consumer; see licenses/roots-structured-ten-drivers-MIT.txt.
program main
   use iso_fortran_env,only:wp=>real64
   use ieee_arithmetic,only:ieee_is_finite
   use SpecialMatrices,only:Strang,eigh,eigvalsh
   implicit none
   real(wp),allocatable::w(:),v(:,:),z(:),a(:,:)
   real(wp)::pi
   integer::n,i,j,k
   pi=acos(-1._wp)
   do n=2,18
      allocate(a(n,n));a=0
      do i=1,n
         a(i,i)=2
         if(i<n) then
            a(i,i+1)=-1;a(i+1,i)=-1
         end if
      end do
      call eigh(Strang(n),w,v);z=eigvalsh(Strang(n))
      do j=1,n
         call check(w(j),4*sin(pi*j/(2*(n+1)))**2);call check(z(j),w(j))
         do i=1,n
            call check(dot_product(a(i,:),v(:,j)),w(j)*v(i,j))
            call check(dot_product(v(:,i),v(:,j)),real(merge(1,0,i==j),wp))
         end do
      end do
      deallocate(a,w,v,z)
   end do
   print '(a)', '17 Strang spectra: analytic eigenvalues, residuals and orthogonality checked.'
   print '(a)', 'PASS specialmatrices-strang-eigenpairs-reference'
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
