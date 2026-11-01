! Independent MIT consumer; see licenses/pca-ordering-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64, int32, int64
   use ieee_arithmetic, only: ieee_is_finite
   use stdlib_selection, only: select
   implicit none
   real(real64),allocatable :: a(:),original(:),reference(:)
   integer,allocatable :: order(:)
   integer(int32),allocatable :: indices(:)
   real(real64) :: value
   integer :: n,t,k,i,index,calls
   calls=0
   do n=1,31
      allocate(a(n),original(n),reference(n),order(n),indices(n))
      do t=1,6
         call fill(original,t)
         reference=original
         call reference_sort(reference,order,.false.)
         do k=1,n
            a=original
            call select(a,k,value)
            if(.not.ieee_is_finite(value).or.value/=reference(k)) error stop 'Known order statistic'
            if(a(k)/=value) error stop 'Selection pivot'
            if(any(a(:k-1)>value).or.any(a(k+1:)<value)) error stop 'Selection partition'
            do i=1,n
               if(count(a==original(i))/=count(original==original(i))) error stop 'Selection multiset'
            end do
            calls=calls+1
         end do
      end do
      deallocate(a,original,reference,order,indices)
   end do
   print '(a,i0)', 'Every rank on 186 finite duplicate-containing arrays versus independent insertion sort: ',calls
   print '(a)', 'PASS stdlib-select-reference'
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
   subroutine reference_sort(values,order,reverse)
      real(real64),intent(inout) :: values(:)
      integer,intent(out) :: order(:)
      logical,intent(in) :: reverse
      real(real64) :: key
      integer :: i,j,index
      do i=1,size(values)
         order(i)=i
      end do
      do i=2,size(values)
         key=values(i); index=order(i); j=i-1
         do while(j>=1)
            if(reverse) then
               if(values(j)>=key) exit
            else
               if(values(j)<=key) exit
            end if
            values(j+1)=values(j); order(j+1)=order(j); j=j-1
         end do
         values(j+1)=key; order(j+1)=index
      end do
   end subroutine
end program
