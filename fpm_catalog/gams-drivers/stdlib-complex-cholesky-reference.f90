! Independent MIT consumer; see licenses/complex-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64, int64
   use ieee_arithmetic, only: ieee_is_finite
   use stdlib_linalg_constants, only: ilp
   use stdlib_linalg, only: cholesky, linalg_state_type
   implicit none

   complex(real64),allocatable :: l(:,:),a(:,:),saved(:,:),factor(:,:)
   type(linalg_state_type) :: state
   integer :: n,i,j,k,s,count
   count=0
   do n=1,8
      allocate(l(n,n),a(n,n),saved(n,n),factor(n,n))
      do k=1,3
         do s=-1,1
            l=0
            do i=1,n
               l(i,i)=n+i
               do j=1,i-1
                  l(i,j)=cmplx(real(i+j+k,real64)/16,real(i-j,real64)/32,real64)
               end do
            end do
            l=l*2._real64**(2*s); saved=matmul(l,conjg(transpose(l)))
            a=saved
            call cholesky(a,factor,lower=.true.,err=state)
            if(state%error()) error stop 'Complex Cholesky lower error'
            call check_matrix(factor,l)
            call check_matrix(matmul(factor,conjg(transpose(factor))),saved)
            if(any(a/=saved)) error stop 'Cholesky lower input preservation'
            call cholesky(a,factor,lower=.false.,err=state)
            if(state%error()) error stop 'Complex Cholesky upper error'
            call check_matrix(factor,conjg(transpose(l)))
            call check_matrix(matmul(conjg(transpose(factor)),factor),saved)
            if(any(a/=saved)) error stop 'Cholesky upper input preservation'
            count=count+2
         end do
      end do
      deallocate(l,a,saved,factor)
   end do
   print '(a,i0)', 'Known-factor complex Cholesky lower/upper factorizations: ',count
   print '(a)', 'PASS stdlib-complex-cholesky-reference'
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
