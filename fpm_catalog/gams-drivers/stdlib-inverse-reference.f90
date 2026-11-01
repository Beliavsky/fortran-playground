! Independent MIT consumer; see licenses/statistics-services-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64
   use ieee_arithmetic, only: ieee_is_finite
   use stdlib_linalg, only: inv,linalg_state_type
   implicit none
   type(linalg_state_type) :: state
   real(real64),allocatable :: actual(:,:)
   real(real64) :: a(3,3),original(3,3),expected(3,3),identity(3,3),u(3),v(3),d(3),e(3),denominator
   integer :: t,i,j
   u=[1._real64,-1._real64,2._real64]
   d=[1._real64,2._real64,4._real64]
   e=[2._real64,1._real64,0.5_real64]
   identity=0
   do i=1,3
      identity(i,i)=1
   end do
   do t=1,128
      v=real([1+mod(t,3),1+mod(t/3,4),1+mod(t/12,5)],real64)/8
      denominator=1+sum(u*v)
      do j=1,3
         do i=1,3
            a(i,j)=d(i)*(identity(i,j)+u(i)*v(j))*e(j)
            expected(i,j)=(identity(i,j)-u(i)*v(j)/denominator)/(e(i)*d(j))
         end do
      end do
      original=a
      actual=inv(a,err=state)
      if(.not.state%ok()) error stop 'Inverse status'
      if(.not.all(ieee_is_finite(actual))) error stop 'Nonfinite inverse'
      if(any(abs(actual-expected)>2.e-12_real64)) error stop 'Rank-one inverse oracle'
      if(maxval(abs(matmul(a,actual)-identity))>2.e-12_real64) error stop 'Left inverse residual'
      if(maxval(abs(matmul(actual,a)-identity))>2.e-12_real64) error stop 'Right inverse residual'
      if(any(a/=original)) error stop 'Input overwritten'
   end do
   print '(a)', '128 scaled nonsymmetric rank-one inverses; 1,152 exact-form references and two-sided residuals'
   print '(a)', 'PASS stdlib-inverse-reference'
end program
