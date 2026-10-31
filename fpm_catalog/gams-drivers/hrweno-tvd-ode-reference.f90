! Independent API consumer; MIT: licenses/inverse-tvd-drivers-MIT.txt.
module tvd_reference_problem
   use hrweno_kinds, only: rk
   implicit none
contains
   subroutine rhs(t,u,du)
      real(rk), intent(in) :: t,u(:)
      real(rk), intent(out) :: du(:)
      du = [-u(1),-2*u(2),2*t]
   end subroutine rhs
end module tvd_reference_problem

program tvd_ode_reference
   use tvd_reference_problem
   use hrweno_tvdode, only: rktvd
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer, parameter :: steps(*) = [8,16,32,64]
   real(rk), parameter :: finest_bounds(*) = [.01_rk,.0001_rk,.000001_rk]
   type(rktvd) :: solver
   real(rk) :: u(3),time,h,expected(3),errors(4),ratio,lambda,z,polynomial,max_discrete_error
   integer :: order,grid,i,j,n,runs
   runs = 0
   max_discrete_error = 0._rk
   do order = 1,3
      do grid = 1,size(steps)
         n = steps(grid)
         h = 1._rk/n
         solver = rktvd(rhs,3,order=order)
         u = [1._rk,2._rk,0._rk]
         time = 0._rk
         do i = 1,n
            ! Explicit single-step mode avoids the ordinary mode's final-step overshoot policy.
            call solver%integrate(u,time,time+2*h,h,itask=2)
            if (abs(time-real(i,rk)*h) > 1.e-14_rk) error stop 'single-step time'
         end do
         if (solver%istate /= 2 .or. solver%fevals /= order*n) error stop 'TVD state/evaluation count'
         if (.not. all(ieee_is_finite(u))) error stop 'nonfinite ODE solution'
         do j = 1,2
            lambda = real(j,rk)
            z = -lambda*h
            polynomial = 1+z
            if (order >= 2) polynomial = polynomial+z*z/2
            if (order >= 3) polynomial = polynomial+z*z*z/6
            expected(j) = real(j,rk)*polynomial**n
         end do
         expected(3) = 1._rk
         if (order == 1) expected(3) = 1-h
         max_discrete_error = max(max_discrete_error,maxval(abs(u-expected)))
         if (maxval(abs(u-expected)) > 2.e-12_rk) error stop 'independent discrete reference'
         errors(grid) = maxval(abs(u(:2)-[exp(-1._rk),2*exp(-2._rk)]))
         if (.not. ieee_is_finite(errors(grid)) .or. errors(grid) <= 0) error stop 'continuous ODE error'
         if (grid > 1) then
            ratio = errors(grid-1)/errors(grid)
            if (ratio < .7_rk*2**order .or. ratio > 1.5_rk*2**order) error stop 'convergence order'
         end if
         print '(a,i0,a,i0,a,es12.4)', 'Order=',order,' steps=',n,' continuous error=',errors(grid)
         runs = runs+1
      end do
      if (errors(4) > finest_bounds(order)) error stop 'finest-grid error'
   end do
   if (runs /= 12) error stop 'ODE run count'
   print '(a,es12.4)', 'Maximum error against independent discrete references: ',max_discrete_error
   print '(a)', '12 ODE runs: orders 1..3, exponential decay, nonautonomous forcing and grid convergence.'
   print '(a)', 'PASS hrweno-tvd-ode-reference'
end program tvd_ode_reference
