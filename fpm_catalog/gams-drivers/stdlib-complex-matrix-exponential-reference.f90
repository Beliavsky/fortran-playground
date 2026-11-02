! Independent MIT consumer; see licenses/complex-operators-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64, int64
   use ieee_arithmetic, only: ieee_is_finite
   use stdlib_linalg_constants, only: ilp
   use stdlib_linalg, only: expm, linalg_state_type
   implicit none

   complex(real64),allocatable :: a(:,:),nilpotent(:,:),term(:,:),polynomial(:,:),expected(:,:),result(:,:),saved(:,:)
   complex(real64) :: lambda
   integer :: n,k,s,j,mode,count
   count=0
   do n=2,7
      allocate(nilpotent(n,n))
      do k=1,3
         do s=-2,2
            nilpotent=0
            do j=1,n-1
               nilpotent(j,j+1)=cmplx(real(k+j,real64)/16,real(k-j,real64)/32,real64)*2._real64**s
            end do
            lambda=cmplx(real(k-2,real64)/8,real(s,real64)/16,real64)
            polynomial=identity(n); term=identity(n)
            do j=1,n-1
               term=matmul(term,nilpotent)/real(j,real64); polynomial=polynomial+term
            end do
            call check_matrix(matmul(term,nilpotent),0*identity(n))
            expected=exp(lambda)*polynomial; a=lambda*identity(n)+nilpotent; saved=a
            do mode=1,2
               if(mode==1) then
                  result=expm(a)
               else
                  result=expm(a,order=12_ilp)
               end if
               call check_matrix(result,expected)
               if(any(a/=saved)) error stop 'Matrix exponential input preservation'
               count=count+1
            end do
         end do
      end do
      deallocate(nilpotent)
   end do
   print '(a,i0)', 'Finite-polynomial complex matrix exponentials, default/order 12: ',count
   print '(a)', 'PASS stdlib-complex-matrix-exponential-reference'
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
