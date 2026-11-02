! Independent MIT consumer; see licenses/roots-structured-ten-drivers-MIT.txt.
program main
   use iso_fortran_env,only:wp=>real64
   use ieee_arithmetic,only:ieee_is_finite
   use SpecialMatrices,only:Circulant,svdvals
   implicit none
   real(wp),allocatable::c(:),a(:,:)
   real(wp),allocatable::s(:),ref(:)
   real(wp)::t
   complex(wp)::z
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
      s=svdvals(Circulant(c));allocate(ref(n))
      do j=1,n
         z=cmplx(0._wp,0._wp,wp)
         do k=1,n
            theta=-2*pi*(j-1)*(k-1)/n
            z=z+c(k)*cmplx(cos(theta),sin(theta),wp)
         end do
         ref(j)=abs(z)
      end do
      do i=2,n
         t=ref(i);j=i-1
         do while(j>=1)
            if(ref(j)>=t) exit
            ref(j+1)=ref(j);j=j-1
         end do
         ref(j+1)=t
      end do
      do i=1,n
         call check(s(i),ref(i))
      end do
      deallocate(c,a,s,ref)
   end do
   print '(a)', '15 nonsymmetric real circulants, dimensions 3..17, independently checked.'
   print '(a)', 'PASS specialmatrices-circulant-singular-values-reference'
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
