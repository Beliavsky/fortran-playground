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
      y=(x-center)**power
   end function
end module
program main
   use integrand_data
   use quadpack, only: dqawc
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer,parameter :: limit=300,lenw=4*limit
   real(wp) :: result,abserr,work(lenw),expected,a,b
   integer :: ier,neval,last,iwork(limit),i,j,k,cases

   cases=0
   do i=1,3
      a=-real(i-1,wp); b=real(i,wp)
      do j=1,3
         center=a+real(j,wp)*(b-a)/4
         do power=0,3
            if(power==0) then
               expected=log((b-center)/(center-a))
            else
               expected=((b-center)**power-(a-center)**power)/real(power,wp)
            end if
            call dqawc(f,a,b,center,1.e-10_wp,1.e-10_wp,result,abserr,neval,ier,limit,lenw,last,iwork,work)
            call status_check(); call check(result,expected); cases=cases+1
         end do
      end do
   end do
   print '(a,i0)', 'Cauchy principal values with polynomial numerators: ',cases
   print '(a)', 'PASS quadpack-cauchy-principal-values-reference'
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
