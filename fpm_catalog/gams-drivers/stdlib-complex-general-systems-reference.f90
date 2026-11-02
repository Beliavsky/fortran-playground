! Independent MIT consumer; see licenses/complex-operators-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64, int64
   use ieee_arithmetic, only: ieee_is_finite
   use stdlib_linalg_constants, only: ilp
   use stdlib_linalg, only: solve, linalg_state_type
   implicit none

   complex(real64),allocatable :: a(:,:),saved(:,:),b(:,:),bsaved(:,:),x(:,:),expected(:,:),v(:)
   type(linalg_state_type) :: state
   integer :: n,k,s,i,j,count
   count=0
   do n=1,8
      allocate(saved(n,n),expected(n,3))
      do k=1,3
         do s=-1,1
            do j=1,n
               do i=1,n
                  saved(n+1-i,j)=cmplx(real(i-2*j,real64)/32,real(i+j+k,real64)/32,real64)
                  if(i==j) saved(n+1-i,j)=cmplx(real(n+i+2,real64),real(k,real64)/4,real64)
               end do
            end do
            saved=saved*2._real64**s
            do j=1,3
               do i=1,n
                  expected(i,j)=cmplx(real(i-j,real64)/4,real(i+j+k,real64)/8,real64)
               end do
            end do
            b=matmul(saved,expected); bsaved=b; a=saved
            x=solve(a,b,overwrite_a=.false.,err=state)
            if(state%error()) error stop 'Complex multiple-RHS solve error'
            call check_matrix(x,expected); call check_matrix(matmul(saved,x),bsaved)
            if(any(a/=saved).or.any(b/=bsaved)) error stop 'Complex system preservation'
            v=solve(a,b(:,1),overwrite_a=.false.,err=state)
            if(state%error()) error stop 'Complex vector solve error'
            do i=1,n
               call checkz(v(i),expected(i,1))
               call checkz(sum(saved(i,:)*v),bsaved(i,1))
            end do
            if(any(a/=saved)) error stop 'Complex vector system preservation'
            count=count+2
         end do
      end do
      deallocate(saved,expected)
   end do
   print '(a,i0)', 'Manufactured general complex vector and multiple-RHS linear solves: ',count
   print '(a)', 'PASS stdlib-complex-general-systems-reference'
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
