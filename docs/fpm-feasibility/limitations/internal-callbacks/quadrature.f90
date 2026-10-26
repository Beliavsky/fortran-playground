! Integrate x**2 over [0,1]; verify the result rather than only printing it.
program demo
   use iso_fortran_env, only: wp => real64
   use quadrature_module, only: integration_class_1d
   implicit none
   type(integration_class_1d) :: integral
   real(wp) :: answer, estimate
   integer :: status
   call integral%initialize(fx=square, xl=0.0_wp, xu=1.0_wp, tolx=1.0e-10_wp, methodx=8)
   call integral%integrate(answer, status, estimate)
   if (abs(answer - 1.0_wp/3.0_wp) > 1.0e-9_wp) error stop 'incorrect integral'
   print '(a,f15.12,a,i0)', 'PASS quadrature integral=', answer, ' status=', status
contains
   function square(me, x) result(y)
      class(integration_class_1d), intent(inout) :: me
      real(wp), intent(in) :: x
      real(wp) :: y
      y = x*x
   end function square
end program demo
