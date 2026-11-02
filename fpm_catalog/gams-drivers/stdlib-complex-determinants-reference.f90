! Independent MIT consumer; see licenses/complex-operators-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64, int64
   use ieee_arithmetic, only: ieee_is_finite
   use stdlib_linalg_constants, only: ilp
   use stdlib_linalg, only: det, linalg_state_type
   implicit none

   complex(real64),allocatable :: q(:,:),d(:,:),a(:,:),saved(:,:),shifted(:,:)
   complex(real64) :: expected,value
   type(linalg_state_type) :: state
   integer :: n,k,s,i,count
   count=0
   do n=1,8
      allocate(d(n,n),a(n,n),shifted(n,n))
      do k=1,3
         q=unitary(n,k)
         do s=-1,1
            d=0; expected=1
            do i=1,n
               d(i,i)=cmplx(1._real64+real(i,real64)/4,real(k-i,real64)/8,real64)*2._real64**s
               expected=expected*d(i,i)
            end do
            a=matmul(q,matmul(d,conjg(transpose(q))))
            do i=1,n
               shifted(i,:)=a(mod(i,n)+1,:)
            end do
            if(mod(n-1,2)==1) expected=-expected
            saved=shifted
            value=det(shifted,err=state)
            if(state%error()) error stop 'Complex determinant API error'
            call checkz(value,expected)
            if(any(shifted/=saved)) error stop 'Determinant input preservation'
            count=count+1
         end do
      end do
      deallocate(d,a,shifted)
   end do
   print '(a,i0)', 'Complex determinants versus diagonal products and cyclic permutation signs: ',count
   print '(a)', 'PASS stdlib-complex-determinants-reference'
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
