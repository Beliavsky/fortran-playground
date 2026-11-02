! Independent MIT consumer; see licenses/forlab-statistics-ten-drivers-MIT.txt.
program main
   use iso_fortran_env,only:dp=>real64
   use ieee_arithmetic,only:ieee_is_finite
   use forlab,only:wp=>RPRE,chi2pdf,chi2cdf
   implicit none
   real(wp),parameter::points(*)=[0.125_wp,0.5_wp,1._wp,2._wp,4._wp,8._wp]
   real(dp)::t,term,total,factorial,pdf,cdf
   integer::shape,i,k
   if(storage_size(0._wp)/=32) error stop 'Expected pinned Forlab REAL32 kind'
   do shape=1,4
      do i=1,size(points)
         t=real(points(i),dp)/2;total=1;term=1;factorial=1
         do k=1,shape-1
            factorial=factorial*k;term=term*t/k;total=total+term
         end do
         pdf=t**(shape-1)*exp(-t)/(2*factorial);cdf=1-exp(-t)*total
         call check(chi2pdf(points(i),2*shape),pdf)
         call check(chi2cdf(points(i),2*shape),cdf)
      end do
   end do
   print '(a)', '24 even-degree chi-square PDF/CDF cases independently checked.'
   print '(a,i0)', 'Forlab real storage bits: ',storage_size(0._wp)
   print '(a)', 'PASS forlab-even-chi-square-reference'
contains
   subroutine check(actual,reference)
      real(wp),intent(in)::actual
      real(dp),intent(in)::reference
      if(.not.ieee_is_finite(actual)) error stop 'Nonfinite result'
      if(abs(real(actual,dp)-reference)>3.e-5_dp*max(1._dp,abs(reference))) then
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
