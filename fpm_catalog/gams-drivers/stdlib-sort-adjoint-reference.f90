! Independent MIT consumer; see licenses/pca-ordering-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64, int32, int64
   use ieee_arithmetic, only: ieee_is_finite
   use stdlib_sorting, only: sort_adjoint
   use stdlib_sorting, only: int_index
   implicit none
   real(real64),allocatable :: a(:),original(:),reference(:),adjoint(:)
   integer,allocatable :: order(:)
   integer(int_index),allocatable :: indices(:)
   integer :: n,t,i,direction,calls
   logical :: reverse
   calls=0
   do n=0,64
      allocate(a(n),original(n),reference(n),adjoint(n),order(n),indices(n))
      do t=1,6
         call fill(original,t)
         do direction=1,2
            reverse=direction==2
            a=original; reference=original
            call reference_sort(reference,order,reverse)
            adjoint=[(1000._real64+i/8._real64,i=1,n)]
            call sort_adjoint(a,adjoint,reverse=reverse)
            if(any(adjoint/=1000._real64+real(order,real64)/8)) error stop 'Stable associated payload'
            if(any(a/=reference)) error stop 'Independent sorted keys'
            if(.not.all(ieee_is_finite(a))) error stop 'Nonfinite sorted keys'
            calls=calls+1
         end do
      end do
      deallocate(a,original,reference,adjoint,order,indices)
   end do
   print '(a,i0)', 'Stable ascending/descending key and association comparisons, lengths 0..64: ',calls
   print '(a)', 'PASS stdlib-sort-adjoint-reference'
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
