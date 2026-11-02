! Independent MIT consumer; see licenses/forlab-statistics-ten-drivers-MIT.txt.
program main
   use iso_fortran_env,only:dp=>real64
   use ieee_arithmetic,only:ieee_is_finite
   use forlab,only:wp=>RPRE,mean,var,std
   implicit none
   real(wp),allocatable::x(:),work(:),values(:),a(:,:),c(:,:)
   real(dp),allocatable::z(:),sorted(:),centered(:),reference(:,:)
   real(dp)::average,m2,m3,m4,expected,position,fraction
   integer,parameter::percentiles(*)=[0,10,25,50,75,90,100]
   integer::n,i,j,k,normalization,variant,index
   if(storage_size(0._wp)/=32) error stop 'Expected pinned Forlab REAL32 kind'
   do n=2,33
      allocate(x(n),z(n),sorted(n),centered(n))
      do variant=1,3
         do i=1,n
            z(i)=real(modulo(7*i+3*n,17)-8,dp)/4
         end do
         select case(variant)
         case(1)
            z=z+1.25_dp
         case(2)
            z=-2*z-0.5_dp
         case(3)
            z=0.5_dp*z+3
         end select
         x=real(z,wp);sorted=z;call insertion_sort(sorted)
         average=sum(z)/n;centered=z-average
         m2=sum(centered**2)/n;m3=sum(centered**3)/n;m4=sum(centered**4)/n
         call check(mean(x),average)
         do normalization=0,1
            expected=sum(centered**2)/real(n-1+normalization,dp)
            call check(var(x,normalization),expected)
            call check(std(x,normalization),sqrt(expected))
         end do
      end do
      deallocate(x,z,sorted,centered)
   end do
   print '(a)', 'Three dyadic affine data families, sizes through 33, independently checked.'
   print '(a,i0)', 'Forlab real storage bits: ',storage_size(0._wp)
   print '(a)', 'PASS forlab-location-dispersion-reference'
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
