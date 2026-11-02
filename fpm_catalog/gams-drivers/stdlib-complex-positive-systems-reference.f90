! Independent MIT consumer; see licenses/complex-operators-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64, int64
   use ieee_arithmetic, only: ieee_is_finite
   use stdlib_linalg_constants, only: ilp
   use stdlib_linalg, only: solve_chol, linalg_state_type
   implicit none

   complex(real64),allocatable :: l(:,:),a(:,:),saved(:,:),expected(:,:),b(:,:),bsaved(:,:),x(:,:),v(:)
   type(linalg_state_type) :: state
   integer :: n,k,s,i,j,triangle,count
   count=0
   do n=1,8
      allocate(l(n,n),expected(n,3),x(n,3),v(n))
      do k=1,3
         do s=-1,1
            l=0
            do i=1,n
               l(i,i)=n+i
               do j=1,i-1
                  l(i,j)=cmplx(real(i+j+k,real64)/16,real(i-j,real64)/32,real64)
               end do
            end do
            l=l*2._real64**s; saved=matmul(l,conjg(transpose(l)))
            do j=1,3
               do i=1,n
                  expected(i,j)=cmplx(real(i-j,real64)/4,real(i+j+k,real64)/8,real64)
               end do
            end do
            b=matmul(saved,expected); bsaved=b
            do triangle=0,1
               a=saved; x=0
               call solve_chol(a,b,x,lower=triangle==0,overwrite_a=.false.,err=state)
               if(state%error()) error stop 'Positive complex multiple-RHS solve error'
               call check_matrix(x,expected); call check_matrix(matmul(saved,x),bsaved)
               if(any(a/=saved).or.any(b/=bsaved)) error stop 'Positive system preservation'
               v=0
               call solve_chol(a,b(:,1),v,lower=triangle==0,overwrite_a=.false.,err=state)
               if(state%error()) error stop 'Positive complex vector solve error'
               do i=1,n
                  call checkz(v(i),expected(i,1)); call checkz(sum(saved(i,:)*v),bsaved(i,1))
               end do
               if(any(a/=saved)) error stop 'Positive vector system preservation'
               count=count+2
            end do
         end do
      end do
      deallocate(l,expected,x,v)
   end do
   print '(a,i0)', 'Manufactured positive-definite complex solves, vector/multiple RHS, lower/upper: ',count
   print '(a)', 'PASS stdlib-complex-positive-systems-reference'
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
