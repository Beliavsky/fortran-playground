module example_functions
   use fmin_module, only: fmin
   use iso_fortran_env, only: wp => real64
   implicit none
contains
   function parabola(x) result(y)
      real(wp), intent(in) :: x
      real(wp) :: y
      y = (x-2.0_wp)**2 + 1.0_wp
   end function
end module example_functions

program main
   use example_functions, only: parabola
   use fmin_module, only: fmin
   use iso_fortran_env, only: wp => real64
   implicit none
   real(wp) :: xmin
   xmin = fmin(parabola, -5.0_wp, 5.0_wp, 1.e-9_wp)
   if (abs(xmin-2.0_wp) > 1.e-6_wp) error stop 'incorrect minimum'
   print *, 'Minimum of (x-2)**2 + 1 at x =', xmin
   print *, 'PASS fmin'
end program main
