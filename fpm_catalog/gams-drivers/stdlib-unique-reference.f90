! Independent MIT consumer; see licenses/pca-ordering-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64, int32, int64
   use ieee_arithmetic, only: ieee_is_finite
   use stdlib_sorting, only: unique
   implicit none
   real(real64),allocatable :: a(:),saved(:),output(:),expected(:)
   logical :: seen(-64:64)
   integer :: n,t,i,j,k,calls
   calls=0
   do n=0,64
      allocate(a(n),saved(n))
      do t=1,6
         call fill(a,t); saved=a; seen=.false.
         do i=1,n
            k=nint(8*a(i))
            if(k < -64.or.k>64) error stop 'Oracle bin range'
            seen(k)=.true.
         end do
         allocate(expected(count(seen))); j=0
         do k=-64,64
            if(.not.seen(k)) cycle
            j=j+1; expected(j)=real(k,real64)/8
         end do
         call unique(a,output,sorted_output=.true.,tolerance=0._real64)
         if(size(output)/=size(expected)) error stop 'Unique-set cardinality'
         if(any(output/=expected)) error stop 'Independent sorted membership set'
         if(.not.all(ieee_is_finite(output))) error stop 'Nonfinite unique values'
         if(any(a/=saved)) error stop 'Unique input preservation'
         deallocate(expected)
         calls=calls+1
      end do
      deallocate(a,saved)
   end do
   print '(a,i0)', 'Sorted unique sets versus independent bin membership, including empty arrays: ',calls
   print '(a)', 'PASS stdlib-unique-reference'
contains
   subroutine fill(a,t)
      real(real64),intent(out) :: a(:)
      integer,intent(in) :: t
      integer :: i,n
      n=size(a)
      do i=1,n
         select case(t)
         case(1)
            a(i)=real(i-n/2,real64)/8
         case(2)
            a(i)=real(n+1-i-n/2,real64)/8
         case(3)
            a(i)=-0.5_real64
         case(4)
            a(i)=(-1._real64)**i*mod(i,7)/8
         case(5)
            a(i)=real(mod(17*i+3*t,23)-11,real64)/8
         case(6)
            a(i)=real((i-1)/3,real64)/8
         end select
      end do
   end subroutine
end program
