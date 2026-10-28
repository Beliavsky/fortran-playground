module integrand_module
   implicit none
contains
   function integrand(x) result(value)
      real(8), intent(in) :: x(:)
      real(8) :: value
      value=x(1)*x(2)
   end function
   function bounds(x,dimension) result(interval)
      real(8), intent(in) :: x(:)
      integer, intent(in) :: dimension
      real(8) :: interval(2)
      interval=[0.d0,1.d0]
      if (dimension==2) interval(2)=x(1)**2+1.d0
   end function
end module
program main
   use gauss_leg_mod, only: gauss_leg_nd
   use integrand_module
   implicit none
   real(8) :: value
   value=gauss_leg_nd([4,4],integrand,bounds)
   if (abs(value-7.d0/12)>1d-10) error stop
   print '(a,f16.12)', 'Integral of x*y over 0<x<1, 0<y<1+x*x:',value
   print '(a,f16.12)', 'Exact answer 7/12:                    ',7.d0/12
   print *, 'PASS integrate_fortran'
end program main
