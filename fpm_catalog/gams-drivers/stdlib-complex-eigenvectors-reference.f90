! Independent MIT consumer; see licenses/grids-spectra-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64, int32
   use ieee_arithmetic, only: ieee_is_finite
   use stdlib_linalg, only: eig, linalg_state_type
   implicit none
   complex(real64),allocatable :: a(:,:),b(:,:),saved(:,:),bsaved(:,:),q(:,:),s(:,:),si(:,:),d(:,:)
   complex(real64),allocatable :: lambda(:),known(:),right(:,:),left(:,:),v(:)
   logical,allocatable :: used(:)
   type(linalg_state_type) :: state
   integer :: n,k,scale,i,j,match,count
   count=0
   do n=2,8
      allocate(d(n,n),lambda(n),known(n),right(n,n),left(n,n),used(n))
      do k=1,3
         q=unitary(n,k); s=identity(n); si=identity(n)
         s(1,n)=cmplx(0.5_real64,0.25_real64,real64); si(1,n)=-s(1,n)
         call check_matrix(matmul(s,si),identity(n))
         do scale=-1,1
            d=0
            do i=1,n
               known(i)=cmplx(real(2*i-k,real64)/4,real(i+k,real64)/8,real64)*2._real64**scale
               d(i,i)=known(i)
            end do
            saved=matmul(q,matmul(s,matmul(d,matmul(si,conjg(transpose(q))))))
            bsaved=identity(n); a=saved
            call eig(a,lambda,right=right,left=left,overwrite_a=.false.,err=state)
            if(state%error()) error stop 'Eigenproblem API error'
            used=.false.
            do j=1,n
               match=0
               do i=1,n
                  if(abs(lambda(j)-known(i))<1.e-9_real64.and..not.used(i)) match=i
               end do
               if(match==0) error stop 'Prescribed distinct eigenvalue match'
               used(match)=.true.; call checkz(lambda(j),known(match))
               call check(real(dot_product(right(:,j),right(:,j)),real64),1._real64)
               call check(real(dot_product(left(:,j),left(:,j)),real64),1._real64)
               v=matmul(saved,right(:,j))-lambda(j)*matmul(bsaved,right(:,j))
               do i=1,n
                  call checkz(v(i),cmplx(0._real64,0._real64,real64))
               end do
               v=matmul(conjg(transpose(saved)),left(:,j)) &
                 -conjg(lambda(j))*matmul(conjg(transpose(bsaved)),left(:,j))
               do i=1,n
                  call checkz(v(i),cmplx(0._real64,0._real64,real64))
               end do
            end do
            if(any(a/=saved)) error stop 'Eigenproblem A preservation'
            count=count+1
         end do
      end do
      deallocate(d,lambda,known,right,left,used)
   end do
   print '(a,i0)', 'Distinct prescribed spectra and left/right residuals: ',count
   print '(a)', 'PASS stdlib-complex-eigenvectors-reference'
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
