! Fit exact quadratic data using the rectangular-system solver.
program demo_forlab
   use forlab, only: RPRE,linspace,solve
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   real(RPRE) :: x(5),design(5,3),y(5),coefficients(3),residual
   x = linspace(-2.0_RPRE,2.0_RPRE,5)
   design(:,1) = 1; design(:,2) = x; design(:,3) = x*x
   y = 1.0_RPRE+2.0_RPRE*x-0.5_RPRE*x*x
   coefficients = solve(design,y)
   if (.not. all(ieee_is_finite(coefficients))) error stop 'Nonfinite fit coefficients'
   residual = maxval(abs(matmul(design,coefficients)-y))
   if (residual>1e-4_RPRE) error stop 'Fit residual too large'
   if (maxval(abs(coefficients-[1.0_RPRE,2.0_RPRE,-0.5_RPRE]))>1e-4_RPRE) error stop 'Wrong coefficients'
   print '(a,3f14.7)', 'Fitted constant, linear and quadratic coefficients: ',coefficients
   print '(a,es12.3)', 'Maximum residual: ',residual
   print '(a)', 'PASS forlab'
end program
