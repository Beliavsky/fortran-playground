! Independent MIT consumer; see licenses/statistics-services-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: int64,real64
   use ieee_arithmetic, only: ieee_is_finite
   use stdlib_stats, only: moment
   implicit none
   integer(int64) :: q(32),total,numerator
   real(real64) :: x(32),actual,expected
   integer :: n,shift,i,p,checks
   checks=0
   do n=1,32
      do shift=-4,4
         do i=1,n
            q(i)=mod(7*i+3*n,17)-8+shift
            x(i)=real(q(i),real64)/8
         end do
         total=sum(q(:n))
         do p=3,4
            numerator=0
            do i=1,n
               numerator=numerator+(int(n,int64)*q(i)-total)**p
            end do
            expected=real(numerator,real64)/(real(n,real64)**(p+1)*real(8**p,real64))
            actual=moment(x(:n),order=p)
            call verify()
            numerator=0
            do i=1,n
               numerator=numerator+q(i)**p
            end do
            expected=real(numerator,real64)/real(n*8**p,real64)
            actual=moment(x(:n),order=p,center=0._real64)
            call verify()
         end do
      end do
   end do
   print '(a,i0)', 'Third/fourth moments about mean and zero versus exact integer rational references: ',checks
   print '(a)', 'PASS stdlib-moments-reference'
contains
   subroutine verify()
      if(.not.ieee_is_finite(actual)) error stop 'Nonfinite moment'
      if(abs(actual-expected)>2.e-12_real64*max(1._real64,abs(expected))) error stop 'Rational moment oracle'
      checks=checks+1
   end subroutine
end program
