! Independent MIT consumer; see licenses/grids-spectra-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64, int32
   use ieee_arithmetic, only: ieee_is_finite
   use stdlib_stats_distribution_uniform, only: cdf_uniform
   implicit none
   integer(int32) :: loc,scale,x,j
   real(real64) :: actual,expected,total
   integer :: count,below
   count=0
   do loc=-8,8
      do scale=1,16
         total=0
         do x=loc-2,loc+scale+2
            below=0
            do j=loc,loc+scale
               if(j<=x) below=below+1
            end do
            expected=real(below,real64)/real(scale+1,real64)
            actual=real(cdf_uniform(x,loc,scale),real64)
            if(.not.ieee_is_finite(actual)) error stop 'Nonfinite discrete probability'
            if(abs(actual-expected)>2.e-7_real64) error stop 'Support-count probability'
            total=total+actual; count=count+1
         end do
         if(abs(real(cdf_uniform(loc+scale,loc,scale),real64)-1._real64)>2.e-7_real64) error stop 'CDF endpoint'
      end do
   end do
   print '(a,i0)', 'Inclusive integer uniform support-count comparisons: ',count
   print '(a)', 'PASS stdlib-integer-uniform-cdf-reference'
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
