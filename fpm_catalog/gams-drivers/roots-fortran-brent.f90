! Original checked example using the public roots-fortran object API.
module root_equations
   use iso_fortran_env, only: wp=>real64
   use root_module, only: root_solver
   implicit none
   integer :: problem=1, calls=0, derivative_calls=0
contains
   function value(x) result(y)
      real(wp), intent(in) :: x
      real(wp) :: y
      if (problem==1) then
         y=sin(x)/x
      else
         y=exp(x)-2._wp
      end if
   end function
   function equation(me,x) result(y)
      class(root_solver), intent(inout) :: me
      real(wp), intent(in) :: x
      real(wp) :: y
      calls=calls+1
      y=value(x)
   end function
end module
program checked_scalar_roots
   use root_equations
   use root_module, only: brent_solver
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
   type(brent_solver) :: solver
   integer :: status
   real(wp) :: a,b,x,residual,expected,actual_error
   call solver%initialize(equation,ftol=1.e-12_wp,rtol=1.e-12_wp,atol=1.e-12_wp,maxiter=200)
   do problem=1,2
      if (problem==1) then
         a=1.5_wp; b=5._wp
      else
         a=0._wp; b=2._wp
      end if
      calls=0; derivative_calls=0
      call solver%solve(a,b,x,residual,status)
      if (status/=0) error stop 'roots-fortran status'
      if (.not.ieee_is_finite(x).or..not.ieee_is_finite(residual)) error stop 'nonfinite root/residual'
      if (x<a.or.x>b) error stop 'root outside bracket'
      if (problem==1) then
         expected=acos(-1._wp)
         print '(a)', 'Case: sin(x)/x = 0 on [1.5,5], root pi'
      else
         expected=log(2._wp)
         print '(a)', 'Case: exp(x)-2 = 0 on [0,2], root log(2)'
      end if
      actual_error=abs(x-expected)
      if (actual_error>1.e-9_wp.or.abs(value(x))>1.e-9_wp) error stop 'independent root accuracy'
      if (abs(residual-value(x))>1.e-12_wp) error stop 'reported residual disagreement'
      if (calls<=0) error stop 'missing function evaluations'
      print '(a,es22.14)', 'Computed root: ', x
      print '(a,es12.4)', 'Actual root error: ', actual_error
      print '(a,es12.4)', 'Independent absolute residual: ', abs(value(x))
      print '(a,i0)', 'Function callback calls: ', calls
      print '(a,i0)', 'Derivative callback calls: ', derivative_calls
      print '(a,i0)', 'Solver status: ', status
   end do
   print '(a)', 'PASS roots-fortran-brent'
end program
