module derivative_functions
   use fordiff, only: rk
   implicit none
contains
   function complex_f(x) result(y)
      complex(rk), intent(in) :: x
      complex(rk) :: y
      y=x*x+2._rk*x
   end function
   function real_f(x) result(y)
      real(rk), intent(in) :: x
      real(rk) :: y
      y=x*x+2._rk*x
   end function
end module
program main
   use fordiff, only: derivative
   use derivative_functions
   implicit none
   real(rk) :: cs,central
   cs=derivative(f=complex_f,x=1._rk,h=1e-20_rk)
   central=derivative(f=real_f,x=1._rk,h=1e-5_rk,method='central')
   if (abs(cs-4._rk)>1e-12_rk.or.abs(central-4._rk)>1e-7_rk) error stop
   print *, 'Derivative of x*x+2*x at x=1 (analytic answer: 4)'
   print '(a,f18.12)', 'Complex step:      ',cs
   print '(a,f18.12)', 'Central difference:',central
   print *, 'PASS fordiff'
end program main
