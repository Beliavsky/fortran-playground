! Independent MIT consumer; see licenses/complex-operators-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64, int64
   use ieee_arithmetic, only: ieee_is_finite
   use stdlib_linalg_constants, only: ilp
   use stdlib_linalg, only: solve_weighted_lstsq, linalg_state_type
   implicit none

   complex(real64),allocatable :: q(:,:),a(:,:),saved(:,:),expected(:),b(:),bsaved(:),residual(:),x(:)
   real(real64),allocatable :: weights(:),wsaved(:),rootw(:)
   type(linalg_state_type) :: state
   integer(ilp) :: rank
   integer :: n,m,extra,k,i,j,count
   count=0
   do n=1,5
      do extra=2,4
         m=n+extra
         allocate(saved(m,n),expected(n),residual(m),x(n),weights(m),rootw(m))
         do k=1,3
            q=unitary(m,k)
            rootw=[(2._real64**mod(i+k,3),i=1,m)]; weights=rootw**2; wsaved=weights
            do j=1,n
               saved(:,j)=q(:,j)*real(j+1,real64)/rootw
               expected(j)=cmplx(real(j-k,real64)/4,real(j+k,real64)/8,real64)
            end do
            residual=q(:,n+1)*cmplx(0.5_real64,-0.25_real64,real64)/rootw
            bsaved=matmul(saved,expected)+residual; a=saved; b=bsaved; x=0
            call solve_weighted_lstsq(weights,a,b,x,rank=rank,overwrite_a=.false.,err=state)
            if(state%error()) error stop 'Complex weighted fit API error'
            if(rank/=n) error stop 'Weighted fit rank'
            do j=1,n
               call checkz(x(j),expected(j))
               call checkz(dot_product(saved(:,j),weights*(matmul(saved,x)-b)),cmplx(0._real64,0._real64,real64))
            end do
            do i=1,m
               call checkz(sum(saved(i,:)*x)-b(i),-residual(i))
            end do
            if(any(a/=saved).or.any(b/=bsaved).or.any(weights/=wsaved)) error stop 'Weighted input preservation'
            count=count+1
         end do
         deallocate(saved,expected,residual,x,weights,rootw)
      end do
   end do
   print '(a,i0)', 'Known-coefficient complex weighted fits with nonzero weighted-orthogonal residual: ',count
   print '(a)', 'PASS stdlib-complex-weighted-fits-reference'
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
