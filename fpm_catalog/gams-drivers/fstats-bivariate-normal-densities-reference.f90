! Independent MIT consumer; see licenses/fstats-fitting-ten-drivers-MIT.txt.
program main
   use iso_fortran_env,only:wp=>real64
   use ieee_arithmetic,only:ieee_is_finite
   use fstats_multivariate_normal_distribution,only:multivariate_normal_distribution
   implicit none
   type(multivariate_normal_distribution)::law
   real(wp)::cov(2,2),mu(2),x(2),delta(2),rho,det,q,expected,log_expected
   real(wp),parameter::pi=acos(-1._wp)
   integer::correlation,location,i,j
   do correlation=-1,1
      rho=real(correlation,wp)/2
      cov=reshape([2._wp,rho,rho,1._wp],[2,2]);det=2-rho*rho
      do location=0,1
         mu=[real(location,wp),-real(location,wp)/2]
         call law%initialize(mu,cov)
         do i=-2,2
            do j=-2,2
               delta=[real(i,wp)/2,real(j,wp)/2];x=mu+delta
               q=(delta(1)**2-2*rho*delta(1)*delta(2)+2*delta(2)**2)/det
               log_expected=-log(2*pi)-log(det)/2-q/2
               expected=exp(log_expected)
               call check(law%log_pdf(x),log_expected)
               call check(law%pdf(x),expected)
            end do
         end do
      end do
   end do
   print '(a)', '150 bivariate normal PDF and log-density values independently checked.'
   print '(a)', 'PASS fstats-bivariate-normal-densities-reference'
contains
   subroutine check(actual,expected)
      real(wp),intent(in)::actual,expected
      if(.not.ieee_is_finite(actual)) error stop 'Nonfinite result'
      if(abs(actual-expected)>2.e-10_wp*max(1._wp,abs(expected))) then
         print *, 'Actual, expected:',actual,expected
         error stop 'Independent bivariate density'
      end if
   end subroutine
end program
