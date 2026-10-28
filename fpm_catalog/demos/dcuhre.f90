module playground_dcuhre_functions
   use iso_fortran_env, only: wp => real64
   implicit none
contains
   subroutine integrand(ndim,x,nfun,f)
      integer, intent(in) :: ndim,nfun
      real(wp), intent(in) :: x(ndim)
      real(wp), intent(out) :: f(nfun)
      f(1) = exp(sum(x))
      f(2) = x(1)**2*x(2)*x(3)
   end subroutine
end module

program demo_dcuhre
   use playground_dcuhre_functions, only: wp,integrand
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer, parameter :: ndim=3,nfun=2,nwork=100000
   real(wp) :: lower(ndim),upper(ndim),result(nfun),error(nfun),work(nwork),exact(nfun)
   integer :: evaluations,status,i
   interface
      subroutine dcuhre(ndim,nfun,a,b,minpts,maxpts,fun,epsabs,epsrel,key,nw,restar, &
                        result,abserr,neval,ifail,work)
         import wp,integrand
         integer :: ndim,nfun,minpts,maxpts,key,nw,restar,neval,ifail
         real(wp) :: a(ndim),b(ndim),epsabs,epsrel,result(nfun),abserr(nfun),work(nw)
         procedure(integrand) :: fun
      end subroutine
   end interface
   lower = 0; upper = 1
   exact = [(exp(1.0_wp)-1.0_wp)**3,1.0_wp/12]
   call dcuhre(ndim,nfun,lower,upper,0,100000,integrand,1e-10_wp,1e-8_wp,0,nwork,0, &
      result,error,evaluations,status,work)
   if (status/=0) error stop 'Adaptive integration did not converge'
   if (.not. all(ieee_is_finite(result))) error stop 'Nonfinite integrals'
   if (.not. all(ieee_is_finite(error)) .or. any(error<0)) error stop 'Invalid error estimates'
   if (any(abs(result-exact)>1e-8_wp)) error stop 'Exact integrals differ'
   print '(a)', 'Integrals over the unit cube: exp(x+y+z) and x**2*y*z'
   print '(a)', '       Integral             Exact          Estimated error'
   do i=1,nfun
      print '(3es20.11)',result(i),exact(i),error(i)
   end do
   print '(a,i0)', 'Integrand evaluations: ',evaluations
   print '(a)', 'PASS dcuhre'
end program
