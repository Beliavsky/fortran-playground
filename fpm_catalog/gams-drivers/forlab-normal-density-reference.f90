! Independent MIT consumer; see licenses/forlab-statistics-ten-drivers-MIT.txt.
program main
   use iso_fortran_env,only:dp=>real64
   use ieee_arithmetic,only:ieee_is_finite
   use forlab,only:wp=>RPRE,normpdf
   implicit none
   real(wp)::x(21),y(21),mu,sigma
   real(dp)::expected,t,pi
   integer::im,is,i
   pi=acos(-1._dp)
   if(storage_size(0._wp)/=32) error stop 'Expected pinned Forlab REAL32 kind'
   do im=-1,1
      mu=real(im,wp)
      do is=-1,1
         sigma=2._wp**is
         do i=1,21
            x(i)=mu+sigma*real(i-11,wp)/2
         end do
         y=normpdf(x,mu,sigma)
         do i=1,21
            t=real((x(i)-mu)/sigma,dp)
            expected=exp(-t*t/2)/(sqrt(2*pi)*real(sigma,dp))
            call check(y(i),expected);call check(normpdf(x(i),mu,sigma),expected)
         end do
      end do
   end do
   print '(a)', '189 normal densities; scalar and vector APIs checked.'
   print '(a,i0)', 'Forlab real storage bits: ',storage_size(0._wp)
   print '(a)', 'PASS forlab-normal-density-reference'
contains
   subroutine check(actual,reference)
      real(wp),intent(in)::actual
      real(dp),intent(in)::reference
      if(.not.ieee_is_finite(actual)) error stop 'Nonfinite result'
      if(abs(real(actual,dp)-reference)>3.e-5_dp*max(1.e-20_dp,abs(reference))) then
         print *, 'Actual, reference:',actual,reference
         error stop 'Independent reference'
      end if
   end subroutine
   subroutine matrix_check(actual,reference)
      real(wp),intent(in)::actual(:,:)
      real(dp),intent(in)::reference(:,:)
      integer::i,j
      if(any(shape(actual)/=shape(reference))) error stop 'Matrix shape'
      do j=1,size(actual,2)
         do i=1,size(actual,1)
            call check(actual(i,j),reference(i,j))
         end do
      end do
   end subroutine
   subroutine insertion_sort(x)
      real(dp),intent(inout)::x(:)
      real(dp)::v
      integer::i,j
      do i=2,size(x)
         v=x(i);j=i-1
         do while(j>=1)
            if(x(j)<=v) exit
            x(j+1)=x(j);j=j-1
         end do
         x(j+1)=v
      end do
   end subroutine
   function identity(n) result(a)
      integer,intent(in)::n
      real(dp)::a(n,n)
      integer::i
      a=0
      do i=1,n
         a(i,i)=1
      end do
   end function
end program
