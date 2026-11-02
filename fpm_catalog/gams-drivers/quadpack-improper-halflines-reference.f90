! Independent MIT consumer; see licenses/integrals-tensors-ten-drivers-MIT.txt.
module integrand_data
   use iso_fortran_env, only: wp=>real64
   implicit none
   real(wp) :: rate,center,exponent
   integer :: power
contains
   function f(x) result(y)
      real(wp),intent(in) :: x
      real(wp) :: y
      y=exp(-rate*abs(x))
   end function
end module
program main
   use integrand_data
   use quadpack, only: dqagi
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer,parameter :: limit=300,lenw=4*limit
   real(wp) :: result,abserr,work(lenw),expected,a,b
   integer :: ier,neval,last,iwork(limit),i,j,k,cases

   integer :: direction
   cases=0
   do i=0,3
      rate=2._wp**(i-1)
      do j=0,3
         a=real(j,wp)/2
         do direction=-1,1,2
            expected=exp(-rate*a)/rate
            call dqagi(f,real(direction,wp)*a,direction,1.e-10_wp,1.e-10_wp,result,abserr,neval, &
               ier,limit,lenw,last,iwork,work)
            call status_check(); call check(result,expected); cases=cases+1
         end do
      end do
   end do
   print '(a,i0)', 'Left/right exponential half-line integrals: ',cases
   print '(a)', 'PASS quadpack-improper-halflines-reference'
contains
   subroutine check(actual,expected)
      real(wp),intent(in) :: actual,expected
      if(.not.ieee_is_finite(actual)) error stop 'Nonfinite result'
      if(abs(actual-expected)>2.e-9_wp*max(1._wp,abs(expected))) error stop 'Independent reference'
   end subroutine
   subroutine status_check()
      if(ier/=0) error stop 'QUADPACK unsuccessful status'
      if(neval<=0.or.last<=0) error stop 'QUADPACK work counters'
      if(.not.ieee_is_finite(abserr).or.abserr<0) error stop 'Invalid error estimate'
   end subroutine
end program
