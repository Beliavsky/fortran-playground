! Independent MIT consumer; see licenses/statistics-rank-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64, int64
   use ieee_arithmetic, only: ieee_is_finite
   use stdlib_linalg_constants, only: ilp
   use stdlib_linalg, only: lstsq, linalg_state_type
   implicit none
   complex(real64),allocatable :: q(:,:),p(:,:),d(:,:),a(:,:),saved(:,:),b(:),bsaved(:), &
      expected(:),x(:),coefficients(:),residual(:)
   integer(ilp) :: rank
   type(linalg_state_type) :: state
   integer :: m,n,r,k,extra,i,j,count
   count=0
   do n=3,7
      do extra=2,4
         m=n+extra; r=n-1
         allocate(d(m,n),coefficients(r),expected(n),b(m),residual(m))
         do k=1,3
            q=unitary(m,k); p=unitary(n,k+1); d=0
            do i=1,r
               d(i,i)=i+1
               coefficients(i)=cmplx(real(i-k,real64)/4,real(i+k,real64)/8,real64)
            end do
            expected=matmul(p(:,1:r),coefficients)
            saved=matmul(q,matmul(d,conjg(transpose(p))))
            residual=0
            residual=q(:,r+1)*cmplx(0.25_real64,-0.5_real64,real64)
            b=matmul(saved,expected)+residual; bsaved=b; a=saved
            x=lstsq(a,b,cond=1.e-12_real64,rank=rank,overwrite_a=.false.,err=state)
            if(state%error()) error stop 'Minimum-norm least-squares API error'
            if(rank/=r.or.size(x)/=n) error stop 'Prescribed rank and solution size'
            do i=1,n
               call checkz(x(i),expected(i))
               call checkz(dot_product(saved(:,i),matmul(saved,x)-bsaved),cmplx(0._real64,0._real64,real64))
            end do
            do i=1,m
               call checkz(sum(saved(i,:)*x)-bsaved(i),-residual(i))
            end do
            do j=r+1,n
               call checkz(dot_product(p(:,j),x),cmplx(0._real64,0._real64,real64))
            end do
            if(any(a/=saved).or.any(b/=bsaved)) error stop 'Minimum-norm input preservation'
            count=count+1
         end do
         deallocate(d,coefficients,expected,b,residual)
      end do
   end do
   print '(a,i0)', 'Known minimum-norm solutions, stationarity and null-space orthogonality: ',count
   print '(a)', 'PASS stdlib-complex-rank-deficient-fits-reference'
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
