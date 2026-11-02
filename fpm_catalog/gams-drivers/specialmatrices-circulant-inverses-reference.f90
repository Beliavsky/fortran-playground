! Independent MIT consumer; see licenses/roots-structured-ten-drivers-MIT.txt.
program main
   use iso_fortran_env,only:wp=>real64
   use ieee_arithmetic,only:ieee_is_finite
   use SpecialMatrices,only:Circulant,inv,dense
   implicit none
   real(wp),allocatable::c(:),a(:,:)
   real(wp),allocatable::b(:,:),ab(:,:),ba(:,:)
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
      b=dense(inv(Circulant(c)));ab=matmul(a,b);ba=matmul(b,a)
      do j=1,n
         do i=1,n
            call check(ab(i,j),real(merge(1,0,i==j),wp))
            call check(ba(i,j),real(merge(1,0,i==j),wp))
         end do
      end do
      deallocate(c,a,b,ab,ba)
   end do
   print '(a)', '15 nonsymmetric real circulants, dimensions 3..17, independently checked.'
   print '(a)', 'PASS specialmatrices-circulant-inverses-reference'
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
