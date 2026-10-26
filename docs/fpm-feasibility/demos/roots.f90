! Solve x**2 - 2 = 0 with Brent's method.
! Module callbacks avoid executable-stack trampolines for internal procedures.
module audit_functions
   use iso_fortran_env, only: wp => real64
   use root_module, only: root_solver
   implicit none
contains
   function equation(me, x) result(y)
      class(root_solver), intent(inout) :: me
      real(wp), intent(in) :: x
      real(wp) :: y
      y = x*x - 2.0_wp
   end function equation
end module audit_functions

program demo
   use iso_fortran_env, only: wp => real64
   use root_module, only: brent_solver
   use audit_functions, only: equation
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
   real(wp) :: x, residual
   integer :: status
   type(brent_solver) :: solver
   call solver%initialize(equation, rtol=1.0e-12_wp)
   call solver%solve(0.0_wp, 2.0_wp, x, residual, status)
   if (.not. ieee_is_finite(x)) error stop 'nonfinite root'
   if (status /= 0 .or. abs(x - sqrt(2.0_wp)) > 1.0e-9_wp) error stop 'incorrect root'
   print '(a,f15.12)', 'PASS roots sqrt(2)=', x
end program demo
