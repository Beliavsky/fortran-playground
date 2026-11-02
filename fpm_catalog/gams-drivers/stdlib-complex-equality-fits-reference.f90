! Independent MIT consumer; see licenses/complex-operators-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64, int64
   use ieee_arithmetic, only: ieee_is_finite
   use stdlib_linalg_constants, only: ilp
   use stdlib_linalg, only: solve_constrained_lstsq, linalg_state_type
   implicit none

   complex(real64),allocatable :: q(:,:),a(:,:),saved(:,:),b(:),bsaved(:),c(:,:),csaved(:,:), &
      x(:),expected(:),u(:),row(:),y(:),gradient(:)
   real(real64),allocatable :: diagonal(:),hessian(:)
   complex(real64) :: d(1),dsaved(1),lambda,denominator
   type(linalg_state_type) :: state
   integer :: n,k,s,i,j,count
   count=0
   do n=2,7
      allocate(a(2*n,n),b(2*n),c(1,n),x(n),expected(n),u(n),row(n),y(n),gradient(n),diagonal(n),hessian(n))
      do k=1,4
         q=unitary(n,k)
         do s=-1,1
            do i=1,n
               diagonal(i)=(1._real64+real(i,real64)/4)*2._real64**s
               b(i)=cmplx(real(i-k,real64)/8,real(i+k,real64)/16,real64)
               b(i+n)=cmplx(real(k-2*i,real64)/16,real(2*k+i,real64)/8,real64)
               row(i)=cmplx(1._real64+real(i+k,real64)/8,real(i-k,real64)/16,real64)
            end do
            hessian=5*diagonal**2
            u=(diagonal*b(:n)+2*diagonal*b(n+1:))/hessian
            d(1)=cmplx(real(k-n,real64)/8,real(n+k,real64)/16,real64)
            denominator=sum(row*conjg(row)/hessian)
            lambda=(sum(row*u)-d(1))/denominator
            y=u-conjg(row)*lambda/hessian; expected=matmul(conjg(transpose(q)),y)
            do j=1,n
               a(:n,j)=diagonal*q(:,j); a(n+1:,j)=2*diagonal*q(:,j)
               c(1,j)=sum(row*q(:,j))
            end do
            saved=a; bsaved=b; csaved=c; dsaved=d; x=0
            call solve_constrained_lstsq(a,b,c,d,x,overwrite_matrices=.false.,err=state)
            if(state%error()) error stop 'Complex constrained fit API error'
            do i=1,n
               call checkz(x(i),expected(i))
               gradient(i)=dot_product(saved(:,i),matmul(saved,x)-bsaved)+conjg(csaved(1,i))*lambda
               call checkz(gradient(i),cmplx(0._real64,0._real64,real64))
            end do
            call checkz(sum(csaved(1,:)*x),dsaved(1))
            if(any(a/=saved).or.any(b/=bsaved).or.any(c/=csaved).or.any(d/=dsaved)) &
               error stop 'Constrained input preservation'
            count=count+1
         end do
      end do
      deallocate(a,b,c,x,expected,u,row,y,gradient,diagonal,hessian)
   end do
   print '(a,i0)', 'Closed-form complex equality-constrained KKT minimizers, feasibility and stationarity: ',count
   print '(a)', 'PASS stdlib-complex-equality-fits-reference'
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
