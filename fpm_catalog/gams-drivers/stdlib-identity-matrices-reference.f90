! Independent MIT consumer; see licenses/complex-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64, int64
   use ieee_arithmetic, only: ieee_is_finite
   use stdlib_linalg_constants, only: ilp
   use stdlib_linalg, only: eye
   implicit none

   real(real64),allocatable :: a(:,:)
   complex(real64),allocatable :: z(:,:)
   integer(int64),allocatable :: ia(:,:)
   integer :: m,n,i,j,expected
   do m=0,9
      do n=0,8
         a=eye(m,n); z=eye(m,n,mold=cmplx(0._real64,0._real64,real64)); ia=eye(m,n,mold=0_int64)
         if(any(shape(a)/=[m,n]).or.any(shape(z)/=[m,n]).or.any(shape(ia)/=[m,n])) error stop 'Identity shape'
         do j=1,n
            do i=1,m
               expected=0
               if(i==j) expected=1
               call check(a(i,j),real(expected,real64))
               call checkz(z(i,j),cmplx(real(expected,real64),0._real64,real64))
               if(ia(i,j)/=expected) error stop 'Integer Kronecker delta'
            end do
         end do
      end do
      a=eye(m)
      if(any(shape(a)/=[m,m])) error stop 'Default square identity'
      do j=1,m
         do i=1,m
            expected=0
            if(i==j) expected=1
            call check(a(i,j),real(expected,real64))
         end do
      end do
   end do
   print '(a)', 'Kronecker-delta identity references: 90 rectangles in three kinds and 10 default squares'
   print '(a)', 'PASS stdlib-identity-matrices-reference'
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
