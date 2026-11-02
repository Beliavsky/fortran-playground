! Independent MIT consumer; see licenses/complex-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64, int64
   use ieee_arithmetic, only: ieee_is_finite
   use stdlib_linalg_constants, only: ilp
   use stdlib_linalg, only: hermitian
   implicit none

   real(real64),allocatable :: a(:,:),h(:,:)
   complex(real64),allocatable :: z(:,:),zh(:,:)
   integer :: m,n,i,j
   do m=0,9
      do n=0,8
         allocate(a(m,n),z(m,n))
         do j=1,n
            do i=1,m
               a(i,j)=real(2*i-3*j,real64)/4
               z(i,j)=cmplx(a(i,j),real(i+2*j,real64)/8,real64)
            end do
         end do
         h=hermitian(a); zh=hermitian(z)
         if(any(shape(h)/=[n,m]).or.any(shape(zh)/=[n,m])) error stop 'Conjugate transpose shape'
         do j=1,m
            do i=1,n
               call check(h(i,j),real(2*j-3*i,real64)/4)
               call checkz(zh(i,j),cmplx(real(2*j-3*i,real64)/4,-real(j+2*i,real64)/8,real64))
               if(a(j,i)/=real(2*j-3*i,real64)/4) error stop 'Transpose input preservation'
               if(z(j,i)/=cmplx(a(j,i),real(j+2*i,real64)/8,real64)) error stop 'Complex input preservation'
            end do
         end do
         call check_matrix(hermitian(zh),z)
         deallocate(a,z)
      end do
   end do
   print '(a)', 'Coordinate conjugate-transpose references: 90 real and complex shapes; secondary involution'
   print '(a)', 'PASS stdlib-conjugate-transpose-reference'
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
