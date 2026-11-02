! Independent MIT consumer; see licenses/complex-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64, int64
   use ieee_arithmetic, only: ieee_is_finite
   use stdlib_linalg_constants, only: ilp
   use stdlib_linalg, only: norm
   implicit none

   real(real64) :: v(4),a(4,3),rows(4),cols(3),scale
   complex(real64) :: z(4),za(4,3)
   complex(real64),parameter :: phases(4)=[(1._real64,0._real64),(0._real64,1._real64), &
      (-1._real64,0._real64),(0._real64,-1._real64)]
   integer :: k,j,i
   do k=-8,8
      scale=2._real64**k; v=[3._real64,4._real64,0._real64,12._real64]*scale; z=v*phases
      call check(norm(v,1),19*scale); call check(norm(z,'1'),19*scale)
      call check(norm(v,'2'),13*scale); call check(norm(z,2),13*scale)
      call check(norm(v,'inf'),12*scale); call check(norm(z,'inf'),12*scale)
      call check(norm(v,'-inf'),0._real64); call check(norm(z,'-inf'),0._real64)
      do j=1,3
         a(:,j)=v*j; za(:,j)=z*j
      end do
      call check(norm(a,1),114*scale); call check(norm(za,1),114*scale)
      call check(norm(a,2),13*sqrt(14._real64)*scale)
      call check(norm(za,2),13*sqrt(14._real64)*scale)
      rows=norm(za,2,dim=2); cols=norm(a,2,dim=1)
      do j=1,3
         call check(cols(j),13*j*scale)
      end do
      do i=1,4
         call check(rows(i),abs(v(i))*sqrt(14._real64))
      end do
   end do
   print '(a)', 'Pythagorean vector norms: 17 scales, real/complex, four orders and rank-two reductions'
   print '(a)', 'PASS stdlib-vector-norms-reference'
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
