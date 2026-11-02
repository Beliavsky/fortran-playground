! Independent MIT consumer; see licenses/statistics-rank-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64, int64
   use ieee_arithmetic, only: ieee_is_finite
   use stdlib_linalg_constants, only: ilp
   use stdlib_stats, only: mean
   implicit none
   real(real64),parameter :: refre(3,64)=reshape([ &
      0.0625_real64, 0.1875_real64, 0.3125_real64, -0.0833333333333333333_real64, 0.458333333333333333_real64, &
      0.291666666666666667_real64, 0.3125_real64, 0.15625_real64, 0.0_real64, 0.1875_real64, -0.5_real64, -0.125_real64, &
      0.03125_real64, -0.40625_real64, -0.3125_real64, 0.0833333333333333333_real64, -0.416666666666666667_real64, &
      -0.208333333333333333_real64, -0.25_real64, 0.09375_real64, -0.09375_real64, -0.0416666666666666667_real64, &
      -0.166666666666666667_real64, -0.291666666666666667_real64, 0.05_real64, 0.15_real64, 0.25_real64, &
      -0.0833333333333333333_real64, 0.458333333333333333_real64, 0.291666666666666667_real64, 0.3_real64, 0.225_real64, &
      0.15_real64, 0.208333333333333333_real64, -0.166666666666666667_real64, 0.166666666666666667_real64, 0.125_real64, &
      -0.125_real64, -0.375_real64, 0.1875_real64, -0.0625_real64, -0.3125_real64, -0.05_real64, -0.05_real64, &
      -0.05_real64, -0.0416666666666666667_real64, -0.166666666666666667_real64, -0.291666666666666667_real64, &
      -0.0208333333333333333_real64, 0.125_real64, 0.270833333333333333_real64, -0.15625_real64, 0.34375_real64, &
      0.3125_real64, 0.229166666666666667_real64, 0.270833333333333333_real64, -0.0416666666666666667_real64, &
      0.125_real64, 0.0_real64, -0.125_real64, 0.125_real64, 0.0625_real64, -0.354166666666666667_real64, 0.1875_real64, &
      -0.0625_real64, -0.3125_real64, 0.0208333333333333333_real64, -0.145833333333333333_real64, &
      0.0416666666666666667_real64, 0.0625_real64, -0.28125_real64, -0.09375_real64, -0.0892857142857142857_real64, &
      0.142857142857142857_real64, 0.375_real64, -0.225_real64, 0.325_real64, 0.45_real64, 0.160714285714285714_real64, &
      0.339285714285714286_real64, -0.0892857142857142857_real64, 0.125_real64, 0.0_real64, -0.125_real64, &
      0.107142857142857143_real64, -0.0714285714285714286_real64, -0.25_real64, 0.15_real64, -0.225_real64, &
      -0.175_real64, 0.0535714285714285714_real64, -0.178571428571428571_real64, -0.107142857142857143_real64, &
      0.1_real64, -0.3_real64, -0.275_real64, -0.125_real64, 0.21875_real64, 0.296875_real64, -0.225_real64, &
      0.325_real64, 0.45_real64, 0.125_real64, 0.1875_real64, -0.015625_real64, 0.075_real64, -0.175_real64, 0.0_real64, &
      0.109375_real64, -0.109375_real64, -0.328125_real64, 0.145833333333333333_real64, -0.25_real64, &
      -0.291666666666666667_real64, 0.09375_real64, -0.140625_real64, -0.109375_real64, 0.1_real64, -0.3_real64, &
      -0.275_real64, -0.111111111111111111_real64, 0.125_real64, 0.361111111111111111_real64, -0.1875_real64, &
      0.166666666666666667_real64, 0.520833333333333333_real64, 0.138888888888888889_real64, 0.152777777777777778_real64, &
      -0.0694444444444444444_real64, 0.104166666666666667_real64, -0.166666666666666667_real64, &
      -0.0833333333333333333_real64, 0.152777777777777778_real64, -0.0555555555555555556_real64, &
      -0.263888888888888889_real64, 0.145833333333333333_real64, -0.25_real64, -0.291666666666666667_real64, &
      0.166666666666666667_real64, -0.0277777777777777778_real64, 0.0138888888888888889_real64, &
      0.208333333333333333_real64, -0.104166666666666667_real64, -0.0625_real64, -0.0375_real64, 0.15_real64, &
      0.3375_real64, -0.0714285714285714286_real64, 0.196428571428571429_real64, 0.464285714285714286_real64, &
      0.2125_real64, 0.225_real64, 0.025_real64, 0.104166666666666667_real64, -0.166666666666666667_real64, &
      -0.0833333333333333333_real64, 0.0375_real64, -0.125_real64, -0.2875_real64, -0.0178571428571428571_real64, &
      -0.321428571428571429_real64, -0.321428571428571429_real64, 0.075_real64, -0.05_real64, 0.0375_real64, &
      0.0714285714285714286_real64, -0.125_real64, -0.0178571428571428571_real64, -0.0909090909090909091_real64, &
      0.0909090909090909091_real64, 0.272727272727272727_real64, -0.0714285714285714286_real64, &
      0.196428571428571429_real64, 0.464285714285714286_real64, 0.159090909090909091_real64, 0.204545454545454545_real64, &
      0.0568181818181818182_real64, 0.0357142857142857143_real64, -0.142857142857142857_real64, &
      -0.0178571428571428571_real64, 0.0227272727272727273_real64, -0.0681818181818181818_real64, &
      -0.352272727272727273_real64, -0.03125_real64, -0.21875_real64, -0.40625_real64, 0.0795454545454545455_real64, &
      0.0454545454545454545_real64, 0.0113636363636363636_real64, 0.0714285714285714286_real64, -0.125_real64, &
      -0.0178571428571428571_real64 ],[3,64])
   real(real64),parameter :: refim(3,64)=reshape([ &
      -0.46875_real64, -0.03125_real64, 0.40625_real64, -0.75_real64, -0.291666666666666667_real64, &
      0.166666666666666667_real64, -0.21875_real64, 0.34375_real64, 0.3125_real64, 0.125_real64, 0.6875_real64, &
      0.0625_real64, 0.03125_real64, 0.125_real64, 0.21875_real64, 0.0833333333333333333_real64, &
      -0.0416666666666666667_real64, 0.625_real64, 0.28125_real64, 0.5_real64, -0.46875_real64, 0.0_real64, &
      0.833333333333333333_real64, -0.708333333333333333_real64, -0.6_real64, -0.1_real64, 0.4_real64, -0.75_real64, &
      -0.291666666666666667_real64, 0.166666666666666667_real64, -0.35_real64, 0.275_real64, 0.425_real64, &
      -0.208333333333333333_real64, 0.458333333333333333_real64, 0.333333333333333333_real64, -0.1_real64, 0.175_real64, &
      -0.025_real64, -0.09375_real64, 0.0625_real64, 0.21875_real64, 0.15_real64, 0.55_real64, -0.475_real64, 0.0_real64, &
      0.833333333333333333_real64, -0.708333333333333333_real64, -0.604166666666666667_real64, &
      -0.0416666666666666667_real64, 0.520833333333333333_real64, -0.71875_real64, -0.15625_real64, 0.40625_real64, &
      -0.354166666666666667_real64, 0.333333333333333333_real64, 0.229166666666666667_real64, -0.25_real64, 0.5_real64, &
      0.0625_real64, -0.104166666666666667_real64, 0.3125_real64, -0.0625_real64, -0.09375_real64, 0.0625_real64, &
      0.21875_real64, 0.145833333333333333_real64, 0.291666666666666667_real64, -0.354166666666666667_real64, &
      0.03125_real64, 0.375_real64, -0.46875_real64, -0.464285714285714286_real64, -0.178571428571428571_real64, &
      0.446428571428571429_real64, -0.5_real64, -0.325_real64, 0.325_real64, -0.214285714285714286_real64, &
      0.196428571428571429_real64, 0.267857142857142857_real64, -0.25_real64, 0.5_real64, 0.0625_real64, &
      0.0357142857142857143_real64, 0.232142857142857143_real64, 0.0892857142857142857_real64, 0.1_real64, 0.0_real64, &
      0.375_real64, 0.285714285714285714_real64, 0.267857142857142857_real64, -0.428571428571428571_real64, 0.25_real64, &
      0.325_real64, -0.55_real64, -0.46875_real64, -0.078125_real64, 0.3125_real64, -0.5_real64, -0.325_real64, &
      0.325_real64, -0.21875_real64, 0.296875_real64, 0.21875_real64, -0.25_real64, 0.6_real64, 0.025_real64, &
      0.03125_real64, 0.078125_real64, 0.125_real64, 0.0833333333333333333_real64, -0.166666666666666667_real64, &
      0.375_real64, 0.28125_real64, 0.15625_real64, -0.265625_real64, 0.25_real64, 0.325_real64, -0.55_real64, &
      -0.513888888888888889_real64, -0.0277777777777777778_real64, 0.194444444444444444_real64, -0.5625_real64, &
      -0.208333333333333333_real64, 0.145833333333333333_real64, -0.263888888888888889_real64, &
      0.347222222222222222_real64, 0.166666666666666667_real64, -0.3125_real64, 0.625_real64, &
      -0.0208333333333333333_real64, -0.0138888888888888889_real64, 0.194444444444444444_real64, &
      0.138888888888888889_real64, 0.0833333333333333333_real64, -0.166666666666666667_real64, 0.375_real64, &
      0.236111111111111111_real64, 0.0416666666666666667_real64, -0.152777777777777778_real64, 0.1875_real64, &
      0.125_real64, -0.333333333333333333_real64, -0.5375_real64, 0.0375_real64, 0.1375_real64, &
      -0.589285714285714286_real64, -0.0892857142857142857_real64, 0.0714285714285714286_real64, -0.2875_real64, &
      0.4125_real64, 0.1625_real64, -0.3125_real64, 0.625_real64, -0.0208333333333333333_real64, -0.0375_real64, &
      0.075_real64, 0.1875_real64, 0.0357142857142857143_real64, -0.285714285714285714_real64, &
      0.410714285714285714_real64, 0.2125_real64, -0.025_real64, -0.025_real64, 0.160714285714285714_real64, &
      0.0178571428571428571_real64, -0.125_real64, -0.5_real64, -0.0568181818181818182_real64, &
      0.170454545454545455_real64, -0.589285714285714286_real64, -0.0892857142857142857_real64, &
      0.0714285714285714286_real64, -0.25_real64, 0.318181818181818182_real64, 0.238636363636363636_real64, -0.25_real64, &
      0.446428571428571429_real64, 0.125_real64, 0.0_real64, 0.0454545454545454545_real64, 0.0909090909090909091_real64, &
      0.078125_real64, -0.28125_real64, 0.25_real64, 0.25_real64, -0.0113636363636363636_real64, &
      -0.0568181818181818182_real64, 0.160714285714285714_real64, 0.0178571428571428571_real64, -0.125_real64 ],[3,64])

   complex(real64),allocatable :: x(:,:),saved(:,:)
   logical,allocatable :: mask(:,:)
   integer :: n,k,mode,i,j,index,selected
   complex(real64) :: result(3),expected(3),whole
   index=0
   do n=4,11
      allocate(x(n,3),mask(n,3))
      do k=1,4
         do j=1,3
            do i=1,n
               x(i,j)=cmplx(real(mod(i*i+3*j*i+2*k*j,17)-8,real64)/8, &
                  real(mod(2*i*i+j*i+k*(j+1),19)-9,real64)/8,real64)
            end do
         end do
         saved=x
         do mode=0,1
            index=index+1
            do i=1,n
               mask(i,:)=mode==0.or.mod(i+k,3)/=0
            end do
            selected=count(mask(:,1))

            expected=cmplx(refre(:,index),refim(:,index),real64)
            result=mean(x,dim=1,mask=mask)
            do j=1,3
               call checkz(result(j),expected(j)); call checkz(mean(x(:,j),mask=mask(:,j)),expected(j))
            end do
            result=mean(transpose(x),dim=2,mask=transpose(mask))
            do j=1,3
               call checkz(result(j),expected(j))
            end do
            whole=sum(expected)/3; call checkz(mean(x,mask=mask),whole)
            if(mode==0) then
               result=mean(x,dim=1)
               do j=1,3
                  call checkz(result(j),expected(j))
               end do
            end if

            if(any(x/=saved)) error stop 'Statistics input preservation'
         end do
      end do
      deallocate(x,mask)
   end do
   print '(a,i0)', 'Independent exact-reference complex data selections: ',index
   print '(a)', 'PASS stdlib-complex-means-reference'
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
