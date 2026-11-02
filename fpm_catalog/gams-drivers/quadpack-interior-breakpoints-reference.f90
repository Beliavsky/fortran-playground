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
      y=0
      if(x/=center) y=abs(x-center)**exponent
   end function
end module
program main
   use integrand_data
   use quadpack, only: dqagp
   use ieee_arithmetic, only: ieee_is_finite
   implicit none

   integer,parameter :: limit=300,npts=3,leniw=2*limit+npts,lenw=4*limit+npts
   real(wp) :: result,abserr,work(lenw),points(npts),expected,a,b
   integer :: ier,neval,last,iwork(leniw),i,j,k,cases
   cases=0
   do i=1,2
      a=real(1-i,wp); b=real(i,wp)
      do j=1,3
         center=a+real(j,wp)*(b-a)/4
         do k=0,2
            exponent=real(k,wp)-0.5_wp; points=[center,0._wp,0._wp]
            expected=((center-a)**(exponent+1)+(b-center)**(exponent+1))/(exponent+1)
            call dqagp(f,a,b,npts,points,1.e-10_wp,1.e-10_wp,result,abserr,neval,ier, &
               leniw,lenw,last,iwork,work)
            call status_check(); call check(result,expected); cases=cases+1
         end do
      end do
   end do
   print '(a,i0)', 'Supplied interior breakpoints, cusps and integrable singularities: ',cases
   print '(a)', 'PASS quadpack-interior-breakpoints-reference'
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
