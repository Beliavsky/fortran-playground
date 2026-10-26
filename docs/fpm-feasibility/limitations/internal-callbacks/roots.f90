! Solve x**2 - 2 = 0 with Brent's method.
program demo
   use iso_fortran_env, only: wp => real64
   use root_module, only: root_scalar
   implicit none
   real(wp) :: x, residual
   integer :: status
   call root_scalar('brent', equation, 0.0_wp, 2.0_wp, x, residual, status, rtol=1.0e-12_wp)
   if (status /= 0 .or. abs(x - sqrt(2.0_wp)) > 1.0e-9_wp) error stop 'incorrect root'
   print '(a,f15.12)', 'PASS roots sqrt(2)=', x
contains
   function equation(x) result(y)
      real(wp), intent(in) :: x
      real(wp) :: y
      y = x*x - 2.0_wp
   end function equation
end program demo
