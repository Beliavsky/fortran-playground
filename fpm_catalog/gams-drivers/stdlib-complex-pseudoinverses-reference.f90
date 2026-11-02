! Independent MIT consumer; see licenses/complex-operators-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64, int64
   use ieee_arithmetic, only: ieee_is_finite
   use stdlib_linalg_constants, only: ilp
   use stdlib_linalg, only: pinv, linalg_state_type
   implicit none

   complex(real64),allocatable :: q(:,:),p(:,:),d(:,:),di(:,:),a(:,:),saved(:,:),expected(:,:),result(:,:),left(:,:),right(:,:)
   type(linalg_state_type) :: state
   real(real64) :: value
   integer :: m,n,r,i,k,s,count
   count=0
   do m=2,6
      do n=2,6
         r=min(m,n); q=unitary(m,1); p=unitary(n,3)
         allocate(d(m,n),di(n,m))
         do k=1,2
            do s=-1,1
               d=0; di=0
               do i=1,r
                  value=real(r+1-i,real64)*2._real64**(2*s)
                  if(k==2.and.i==r) value=0
                  d(i,i)=value
                  if(value/=0) di(i,i)=1/value
               end do
               a=matmul(q,matmul(d,conjg(transpose(p)))); saved=a
               expected=matmul(p,matmul(di,conjg(transpose(q))))
               result=pinv(a,rtol=1.e-12_real64,err=state)
               if(state%error()) error stop 'Complex pseudoinverse API error'
               call check_matrix(result,expected)
               left=matmul(a,result); right=matmul(result,a)
               call check_matrix(matmul(left,a),a); call check_matrix(matmul(right,result),result)
               call check_matrix(left,conjg(transpose(left))); call check_matrix(right,conjg(transpose(right)))
               if(any(a/=saved)) error stop 'Pseudoinverse input preservation'
               count=count+1
            end do
         end do
         deallocate(d,di)
      end do
   end do
   print '(a,i0)', 'Known complex pseudoinverses and four Moore-Penrose identities: ',count
   print '(a)', 'PASS stdlib-complex-pseudoinverses-reference'
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
