! Independent MIT consumer; see licenses/complex-operators-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64, int64
   use ieee_arithmetic, only: ieee_is_finite
   use stdlib_linalg_constants, only: ilp
   use stdlib_linalg, only: schur, linalg_state_type
   implicit none

   complex(real64),allocatable :: h(:,:),known(:,:),a(:,:),saved(:,:),t(:,:),z(:,:),values(:),expected(:)
   logical,allocatable :: used(:)
   type(linalg_state_type) :: state
   real(real64) :: distance,best
   integer :: n,k,s,i,j,index,count
   count=0
   do n=2,8
      allocate(known(n,n),t(n,n),z(n,n),values(n),expected(n),used(n))
      do k=1,3
         h=unitary(n,k)
         do s=-1,1
            known=0
            do j=1,n
               expected(j)=cmplx(real(j,real64),real(k-j,real64)/4,real64)*2._real64**s
               known(j,j)=expected(j)
               do i=1,j-1
                  known(i,j)=cmplx(real(i+j,real64)/16,real(k+i-j,real64)/32,real64)*2._real64**s
               end do
            end do
            saved=matmul(h,matmul(known,conjg(transpose(h)))); a=saved
            call schur(a,t,z,values,overwrite_a=.false.,err=state)
            if(state%error()) error stop 'Complex Schur API error'
            used=.false.
            do i=1,n
               best=huge(1._real64); index=0
               do j=1,n
                  if(used(j)) cycle
                  distance=abs(values(i)-expected(j))
                  if(distance<best) then
                     best=distance; index=j
                  end if
               end do
               if(index==0) error stop 'One-to-one Schur eigenvalue matching'
               call checkz(values(i),expected(index)); used(index)=.true.
               call checkz(t(i,i),values(i))
               do j=1,i-1
                  call checkz(t(i,j),cmplx(0._real64,0._real64,real64))
               end do
            end do
            call check_matrix(matmul(conjg(transpose(z)),z),identity(n))
            call check_matrix(matmul(z,matmul(t,conjg(transpose(z)))),saved)
            if(any(a/=saved)) error stop 'Schur input preservation'
            count=count+1
         end do
      end do
      deallocate(known,t,z,values,expected,used)
   end do
   print '(a,i0)', 'Known-spectrum nonnormal complex Schur decompositions: ',count
   print '(a)', 'PASS stdlib-complex-schur-reference'
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
