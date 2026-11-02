! Independent MIT consumer; see licenses/grids-spectra-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64, int32
   use ieee_arithmetic, only: ieee_is_finite
   use stdlib_stats, only: median
   implicit none
   real(real64),parameter :: expected(90)=[ &
      -0.4375_real64, 0.0625_real64, 0.375_real64, 0.1875_real64, -0.125_real64, -0.6875_real64, 0.25_real64, &
      -0.1875_real64, -0.125_real64, -0.25_real64, 0.25_real64, 0.375_real64, 0.75_real64, -0.125_real64, &
      -0.375_real64, 0.25_real64, -0.75_real64, -0.625_real64, -0.125_real64, 0.25_real64, 0.1875_real64, &
      0.75_real64, 0.1875_real64, 0.125_real64, 0.375_real64, -0.1875_real64, -0.625_real64, -0.125_real64, &
      0.125_real64, 0.375_real64, 0.3125_real64, 0.5_real64, -0.375_real64, 0.25_real64, 0.375_real64, &
      -0.625_real64, -0.25_real64, 0.25_real64, 0.375_real64, -0.125_real64, 0.5_real64, -0.375_real64, &
      0.1875_real64, 0.375_real64, -0.625_real64, -0.3125_real64, 0.25_real64, 0.375_real64, -0.125_real64, &
      0.5_real64, 0.0625_real64, 0.1875_real64, 0.0_real64, -0.625_real64, -0.25_real64, 0.25_real64, 0.375_real64, &
      -0.125_real64, 0.5_real64, -0.375_real64, 0.25_real64, 0.375_real64, -0.625_real64, -0.25_real64, 0.25_real64, &
      0.375_real64, -0.125_real64, 0.5_real64, 0.0625_real64, 0.1875_real64, 0.0_real64, -0.625_real64, &
      -0.3125_real64, 0.25_real64, 0.375_real64, -0.125_real64, 0.5_real64, 0.0625_real64, 0.125_real64, 0.0_real64, &
      -0.625_real64, -0.25_real64, 0.25_real64, 0.375_real64, -0.125_real64, 0.5_real64, 0.125_real64, 0.125_real64, &
      -0.125_real64, -0.625_real64 ]
   real(real64),allocatable :: x(:,:),saved(:,:),actual(:),other(:)
   real(real64) :: center(3),value
   logical,allocatable :: mask(:,:)
   integer :: n,k,i,j,index,order,mode,count
   index=0; count=0
   do n=3,12
      allocate(x(n,3),mask(n,3))
      do k=1,3
         do j=1,3
            do i=1,n
               x(i,j)=real(mod(i*i+3*j*i+2*k*j,17)-8,real64)/8
               mask(i,j)=mod(i+j+k,4)/=0
            end do
         end do
         saved=x
         actual=median(x,dim=1,mask=mask)
         other=median(transpose(x),dim=2,mask=transpose(mask))
         do j=1,3
            index=index+1
            call check(actual(j),expected(index)); call check(other(j),expected(index))
            call check(median(x(:,j),dim=1,mask=mask(:,j)),expected(index))
            count=count+1
         end do
         where(.not.mask) x=1234._real64
         other=median(x,dim=1,mask=mask)
         do j=1,3
            call check(other(j),actual(j))
         end do
         x=saved
         if(any(x/=saved)) error stop 'Masked statistics input preservation'
      end do
      deallocate(x,mask)
   end do
   if(index/=size(expected)) error stop 'Reference consumption'
   print '(a,i0)', 'Masked reductions against exact rational references: ',count
   print '(a)', 'PASS stdlib-masked-real-medians-reference'
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
