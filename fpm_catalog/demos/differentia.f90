program main
   use differentia, only: wp, derivative, gradient, jacobian
   implicit none
   real(wp) :: value, slope, expected, grad(2), x(2), values(2), jac(2,2)
   character(:), allocatable :: err
   call derivative(scalar, 2.0_wp, value, slope)
   expected = exp(2.0_wp)*(4*cos(2.0_wp)+8*sin(2.0_wp))
   if (abs(value-(4*exp(2.0_wp)*sin(2.0_wp)+1)) > 1.0e-11_wp) error stop 'function value'
   if (abs(slope-expected) > 1.0e-11_wp) error stop 'derivative'
   print '(a,f16.9)', 'Derivative at x=2: ', slope
   x = [2.0_wp,3.0_wp]
   call gradient(multivariate, x, value, grad, err)
   if (allocated(err)) error stop err
   if (abs(value-17) > 1.0e-12_wp .or. maxval(abs(grad-[13.0_wp,5.0_wp])) > 1.0e-12_wp) &
      error stop 'gradient'
   call jacobian(vector, x, values, jac, err=err)
   if (allocated(err)) error stop err
   if (maxval(abs(values-[10.0_wp,7.0_wp])) > 1.0e-12_wp) error stop 'vector values'
   if (maxval(abs(jac-reshape([3.0_wp,4.0_wp,2.0_wp,1.0_wp],[2,2]))) > 1.0e-12_wp) &
      error stop 'Jacobian'
   print '(a,2f9.3)', 'Gradient: ', grad
   print '(a)', 'Jacobian rows:'
   print '(2f9.3)', jac(1,:),jac(2,:)
   print '(a)', 'PASS differentia'
contains
   function scalar(x) result(y)
      use differentia
      type(dual), intent(in) :: x
      type(dual) :: y
      y = sin(x)*exp(x)*x**2.0_wp + 1.0_wp
   end function
   function multivariate(x) result(y)
      use differentia
      type(dual), target, intent(in) :: x(:)
      type(dual) :: y
      y = x(1)*x(1)*x(2)+x(1)+x(2)
   end function
   subroutine vector(x,y)
      use differentia
      type(dual), target, intent(in) :: x(:)
      type(dual), target, intent(out) :: y(:)
      y(1) = x(1)*x(2)+4.0_wp
      y(2) = x(1)*x(1)+x(2)
   end subroutine
end program main
