! Independent MIT consumer; see licenses/forlab-statistics-ten-drivers-MIT.txt.
program main
   use iso_fortran_env,only:dp=>real64
   use ieee_arithmetic,only:ieee_is_finite
   use forlab,only:wp=>RPRE,diff,cumsum
   implicit none
   real(wp),allocatable::x(:),y(:),reconstructed(:)
   real(dp)::h,t,expected
   integer::n,i,spacing,order
   if(storage_size(0._wp)/=32) error stop 'Expected pinned Forlab REAL32 kind'
   do n=5,20
      allocate(x(n))
      do spacing=1,3
         h=2._dp**(spacing-4)
         do i=1,n
            t=-1+(i-1)*h
            x(i)=real(t**3+2*t*t-3*t+1,wp)
         end do
         do order=1,3
            y=diff(x,order)
            if(size(y)/=n-order) error stop 'Difference size'
            do i=1,size(y)
               t=-1+(i-1)*h
               select case(order)
               case(1)
                  expected=3*t*t+4*t-3+(3*t+2)*h+h*h
               case(2)
                  expected=6*(t+h)+4
               case(3)
                  expected=6
               end select
               call check(y(i)/real(h**order,wp),expected)
            end do
            if(order==1) then
               reconstructed=cumsum(y)+x(1)
               do i=1,n-1
                  call check(reconstructed(i),real(x(i+1),dp))
               end do
               deallocate(reconstructed)
            end if
            deallocate(y)
         end do
      end do
      deallocate(x)
   end do
   print '(a)', '48 cubic grids: three forward differences and cumulative reconstruction checked.'
   print '(a)', 'PASS forlab-polynomial-differences-reference'
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
