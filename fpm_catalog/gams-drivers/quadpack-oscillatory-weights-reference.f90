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
      y=exp(-rate*x)
   end function
end module
program main
   use integrand_data
   use quadpack, only: dqawo
   use ieee_arithmetic, only: ieee_is_finite
   implicit none

   integer,parameter :: limit=300,leniw=2*limit,maxp1=50,lenw=4*limit+25*maxp1
   real(wp),parameter :: frequencies(4)=[0.5_wp,4._wp,32._wp,-4._wp]
   real(wp) :: result,abserr,work(lenw),expected,a,b,omega,denominator
   integer :: ier,neval,last,iwork(leniw),i,j,k,integr,cases,initial_accepts
   cases=0; initial_accepts=0; a=0
   do i=0,2
      rate=2._wp**(i-1)
      do j=0,2
         b=2._wp**(j-1)
         do k=1,4
            omega=frequencies(k); denominator=rate**2+omega**2
            do integr=1,2
               if(integr==1) then
                  expected=(rate+exp(-rate*b)*(-rate*cos(omega*b)+omega*sin(omega*b)))/denominator
               else
                  expected=(omega+exp(-rate*b)*(-rate*sin(omega*b)-omega*cos(omega*b)))/denominator
               end if
               call dqawo(f,a,b,omega,integr,1.e-10_wp,1.e-10_wp,result,abserr,neval,ier, &
                  leniw,maxp1,lenw,last,iwork,work)
               call status_check(); call check(result,expected); cases=cases+1
               if(last==0) initial_accepts=initial_accepts+1
            end do
         end do
      end do
   end do
   print '(a,i0)', 'Finite sine/cosine-weighted exponential integrals: ',cases
   print '(a,i0)', 'Initial-estimate acceptances with last=0: ',initial_accepts
   print '(a)', 'PASS quadpack-oscillatory-weights-reference'
contains
   subroutine check(actual,expected)
      real(wp),intent(in) :: actual,expected
      if(.not.ieee_is_finite(actual)) error stop 'Nonfinite result'
      if(abs(actual-expected)>2.e-9_wp*max(1._wp,abs(expected))) error stop 'Independent reference'
   end subroutine
   subroutine status_check()
      if(ier/=0) error stop 'QUADPACK unsuccessful status'
      if(neval<=0.or.last<0) error stop 'QUADPACK work counters'
      if(.not.ieee_is_finite(abserr).or.abserr<0) error stop 'Invalid error estimate'
   end subroutine
end program
