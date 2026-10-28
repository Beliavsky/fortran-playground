module playground_solver_functions
   use forsolver, only: rk
   implicit none
contains
   function f(x) result(y)
      real(rk), intent(in) :: x
      real(rk) :: y
      y = x**3+x-2.0_rk
   end function
   function df(x) result(y)
      real(rk), intent(in) :: x
      real(rk) :: y
      y = 3.0_rk*x**2+1.0_rk
   end function
   function fc(x) result(y)
      complex(rk), intent(in) :: x
      complex(rk) :: y
      y = x**3+x-2.0_rk
   end function
end module

program demo_forsolver
   use forsolver, only: rk,nlsolver
   use playground_solver_functions, only: f,df,fc
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   type(nlsolver) :: solver
   real(rk) :: roots(3),residuals(3)
   complex(rk) :: z
   integer :: i
   call solver%set_options(nl_method='newton',maxit=100,TolFun=1e-12_rk,verbosity=0)
   call solver%solve(F=f,dFdx=df,x0=2.0_rk,x_sol=roots(1))
   call solver%set_options(nl_method='newton-quasi-fd',fdm_method='central', &
      fdm_tol=1e-6_rk,maxit=100,TolFun=1e-12_rk,verbosity=0)
   call solver%solve(F=f,x0=2.0_rk,x_sol=roots(2))
   call solver%set_options(nl_method='newton-quasi-cs',cs_tol=1e-20_rk, &
      maxit=100,TolFun=1e-12_rk,verbosity=0)
   call solver%solve(F=fc,x0=cmplx(2.0_rk,0.0_rk,rk),x_sol=z)
   roots(3) = real(z,rk)
   residuals = [(abs(f(roots(i))),i=1,3)]
   if (.not. all(ieee_is_finite(roots))) error stop 'Nonfinite root'
   if (abs(aimag(z))>1e-10_rk) error stop 'Unexpected complex root'
   if (any(abs(roots-1.0_rk)>1e-10_rk)) error stop 'Roots differ from exact solution'
   if (any(residuals>1e-10_rk)) error stop 'Residual too large'
   print '(a)', 'Solve x**3+x-2 = 0; the unique real root is 1.'
   print '(a,2es18.9)', 'Analytic derivative: ',roots(1),residuals(1)
   print '(a,2es18.9)', 'Central differences: ',roots(2),residuals(2)
   print '(a,2es18.9)', 'Complex step:        ',roots(3),residuals(3)
   print '(a)', 'PASS forsolver'
end program
