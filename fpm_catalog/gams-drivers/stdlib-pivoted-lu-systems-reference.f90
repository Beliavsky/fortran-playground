! Independent MIT consumer; see licenses/complex-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64, int64
   use ieee_arithmetic, only: ieee_is_finite
   use stdlib_linalg_constants, only: ilp
   use stdlib_linalg, only: solve_lu, linalg_state_type
   implicit none

   real(real64),allocatable :: a(:,:),saved(:,:),b(:,:),x(:,:),expected(:,:),v(:)
   integer(ilp),allocatable :: pivot(:)
   type(linalg_state_type) :: state
   integer :: n,i,j,k,mode,count
   real(real64) :: scale
   count=0
   do n=1,10
      allocate(a(n,n),saved(n,n),b(n,3),x(n,3),expected(n,3),v(n),pivot(n))
      do k=-1,1
         scale=2._real64**(3*k)
         do j=1,n
            do i=1,n
               saved(n+1-i,j)=real(i-2*j,real64)/32
               if(i==j) saved(n+1-i,j)=n+2+i
            end do
         end do
         saved=saved*scale
         do j=1,3
            expected(:,j)=[(real(i-2*j,real64)/4,i=1,n)]
         end do
         b=matmul(saved,expected)
         do mode=0,1
            a=saved; x=0
            call solve_lu(a,b,x,pivot=pivot,overwrite_a=mode==1,err=state)
            if(state%error()) error stop 'LU service API error'
            do j=1,3
               do i=1,n
                  call check(x(i,j),expected(i,j))
                  call check(dot_product(saved(i,:),x(:,j)),b(i,j))
               end do
            end do
            if(any(pivot<1).or.any(pivot>n)) error stop 'LU pivot range'
            if(mode==0.and.any(a/=saved)) error stop 'LU input preservation'
            a=saved; v=0
            call solve_lu(a,b(:,1),v,pivot=pivot,overwrite_a=mode==1,err=state)
            if(state%error()) error stop 'LU vector API error'
            do i=1,n
               call check(v(i),expected(i,1))
            end do
            count=count+2
         end do
      end do
      deallocate(a,saved,b,x,expected,v,pivot)
   end do
   print '(a,i0)', 'Manufactured pivoted LU calls (vector/multiple RHS, preserve/overwrite): ',count
   print '(a)', 'PASS stdlib-pivoted-lu-systems-reference'
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
