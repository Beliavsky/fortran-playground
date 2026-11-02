! Independent MIT consumer; see licenses/complex-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64, int64
   use ieee_arithmetic, only: ieee_is_finite
   use stdlib_linalg_constants, only: ilp
   use stdlib_linalg, only: trace
   implicit none

   real(real64),allocatable :: a(:,:)
   complex(real64),allocatable :: z(:,:)
   integer(int64),allocatable :: ia(:,:)
   integer :: m,n,i,j,r,count
   count=0
   do m=0,9
      do n=0,8
         allocate(a(m,n),z(m,n),ia(m,n)); r=min(m,n)
         do j=1,n
            do i=1,m
               a(i,j)=real(2*i-3*j,real64)/4
               z(i,j)=cmplx(a(i,j),real(i+2*j,real64)/8,real64)
               ia(i,j)=int(2*i-3*j,int64)*10000000000_int64
            end do
         end do
         call check(trace(a),-real(r*(r+1),real64)/8)
         call checkz(trace(z),cmplx(-real(r*(r+1),real64)/8,3._real64*r*(r+1)/16,real64))
         if(trace(ia)/=-int(r*(r+1)/2,int64)*10000000000_int64) error stop 'Closed integer diagonal sum'
         do j=1,n
            do i=1,m
               if(a(i,j)/=real(2*i-3*j,real64)/4) error stop 'Trace input preservation'
               if(z(i,j)/=cmplx(a(i,j),real(i+2*j,real64)/8,real64)) error stop 'Complex trace preservation'
               if(ia(i,j)/=int(2*i-3*j,int64)*10000000000_int64) error stop 'Integer trace preservation'
            end do
         end do
         deallocate(a,z,ia); count=count+1
      end do
   end do
   print '(a,i0,a)', 'Closed-form trace shapes: ',count,'; three kinds including empty rectangles'
   print '(a)', 'PASS stdlib-matrix-trace-reference'
contains
   subroutine check(actual,expected)
      real(real64),intent(in) :: actual,expected
      if(.not.ieee_is_finite(actual)) error stop 'Nonfinite result'
      if(abs(actual-expected)>2.e-10_real64*max(1._real64,abs(expected))) error stop 'Independent reference'
   end subroutine
   subroutine checkz(actual,expected)
      complex(real64),intent(in) :: actual,expected
      call check(real(actual,real64),real(expected,real64))
      call check(aimag(actual),aimag(expected))
   end subroutine
   subroutine check_matrix(actual,expected)
      complex(real64),intent(in) :: actual(:,:),expected(:,:)
      integer :: i,j
      if(any(shape(actual)/=shape(expected))) error stop 'Matrix shape'
      do j=1,size(actual,2)
         do i=1,size(actual,1)
            call checkz(actual(i,j),expected(i,j))
         end do
      end do
   end subroutine
   function identity(n) result(a)
      integer,intent(in) :: n
      complex(real64) :: a(n,n)
      integer :: i
      a=0
      do i=1,n
         a(i,i)=1
      end do
   end function
   function unitary(n,k) result(q)
      integer,intent(in) :: n,k
      complex(real64) :: q(n,n),v(n)
      real(real64) :: denominator
      integer :: i,j
      do i=1,n
         v(i)=cmplx(real(i,real64),real(mod(i+k,4)-2,real64),real64)
      end do
      denominator=real(dot_product(v,v),real64)
      q=identity(n)
      do j=1,n
         do i=1,n
            q(i,j)=q(i,j)-2*v(i)*conjg(v(j))/denominator
         end do
      end do
      call check_matrix(matmul(conjg(transpose(q)),q),identity(n))
   end function
end program
