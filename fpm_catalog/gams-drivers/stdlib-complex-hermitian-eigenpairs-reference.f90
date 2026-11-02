! Independent MIT consumer; see licenses/complex-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64, int64
   use ieee_arithmetic, only: ieee_is_finite
   use stdlib_linalg_constants, only: ilp
   use stdlib_linalg, only: eigh, linalg_state_type
   implicit none

   complex(real64),allocatable :: q(:,:),d(:,:),a(:,:),saved(:,:),vectors(:,:),reconstructed(:,:)
   real(real64),allocatable :: expected(:),values(:)
   type(linalg_state_type) :: state
   integer :: n,i,j,k,s,triangle,count
   count=0
   do n=2,9
      allocate(d(n,n),a(n,n),saved(n,n),vectors(n,n),expected(n),values(n),reconstructed(n,n))
      do k=1,4
         q=unitary(n,k)
         do s=-2,2
            expected=[(real(i-3,real64)*2._real64**s,i=1,n)]; d=0
            do i=1,n
               d(i,i)=expected(i)
            end do
            saved=matmul(q,matmul(d,conjg(transpose(q))))
            do triangle=0,1
               a=saved
               call eigh(a,values,vectors,upper_a=triangle==1,overwrite_a=.false.,err=state)
               if(state%error()) error stop 'Hermitian eigenproblem API error'
               do j=1,n
                  call check(values(j),expected(j))
                  do i=1,n
                     call checkz(sum(saved(i,:)*vectors(:,j)),values(j)*vectors(i,j))
                  end do
               end do
               call check_matrix(matmul(conjg(transpose(vectors)),vectors),identity(n))
               do j=1,n
                  reconstructed(:,j)=vectors(:,j)*values(j)
               end do
               call check_matrix(matmul(reconstructed,conjg(transpose(vectors))),saved)
               if(any(a/=saved)) error stop 'Eigenproblem input preservation'
               count=count+1
            end do
         end do
      end do
      deallocate(d,a,saved,vectors,expected,values,reconstructed)
   end do
   print '(a,i0)', 'Prescribed-spectrum complex Hermitian eigenproblems: ',count
   print '(a)', 'PASS stdlib-complex-hermitian-eigenpairs-reference'
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
