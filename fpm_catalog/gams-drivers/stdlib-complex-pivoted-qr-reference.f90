! Independent MIT consumer; see licenses/statistics-rank-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64, int64
   use ieee_arithmetic, only: ieee_is_finite
   use stdlib_linalg_constants, only: ilp
   use stdlib_linalg, only: qr, linalg_state_type
   implicit none
   complex(real64),allocatable :: a(:,:),saved(:,:),q(:,:),r(:,:)
   complex(real64),allocatable :: h(:,:)
   integer(ilp),allocatable :: pivots(:)
   type(linalg_state_type) :: state
   integer :: m,n,k,i,j,mode,width,calls,permuted
   calls=0; permuted=0
   do m=2,7
      do n=2,6
         allocate(saved(m,n),pivots(n))
         do k=1,3
            h=unitary(m,k)
            saved=0
            do j=1,n
               do i=1,min(j,m)
                  saved(i,j)=cmplx(real(k+i+j,real64)/32,real(i-j,real64)/64,real64)
                  if(i==j) saved(i,j)=1._real64+real(i,real64)/4
               end do
               saved(:,j)=saved(:,j)*2._real64**(j-1)
            end do
            saved=matmul(h,saved)
            do mode=0,1
               width=m
               if(mode==1) width=min(m,n)
               allocate(q(m,width),r(width,n)); a=saved
               call qr(a,q,r,pivots=pivots,overwrite_a=.false.,err=state)
               if(state%error()) error stop 'Pivoted QR API error'
               do j=1,n
                  if(count(pivots==j)/=1) error stop 'Pivot indices must be a permutation'
               end do
               if(any(pivots/=[(i,i=1,n)])) permuted=permuted+1
               call check_matrix(matmul(q,r),saved(:,pivots))
               call check_matrix(matmul(conjg(transpose(q)),q),identity(width))
               do j=1,n
                  do i=j+1,width
                     call checkz(r(i,j),cmplx(0._real64,0._real64,real64))
                  end do
               end do
               if(any(a/=saved)) error stop 'Pivoted QR input preservation'
               calls=calls+1; deallocate(q,r)
            end do
         end do
         deallocate(saved,pivots)
      end do
   end do
   if(permuted==0) error stop 'Pivoting was not exercised'
   print '(a,i0,a,i0)', 'Pivoted QR factorizations: ',calls,'; nonidentity permutations: ',permuted
   print '(a)', 'PASS stdlib-complex-pivoted-qr-reference'
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
