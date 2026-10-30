! Treat the constant decay rate as a second state to differentiate with respect to it.
module decay_problem
   use, intrinsic :: iso_fortran_env, only: real64
   implicit none
contains
   subroutine rhs(n, t, y, f)
      integer, intent(in) :: n
      real(real64), intent(in) :: t, y(n)
      real(real64), intent(out) :: f(n)
      f = [-y(2)*y(1), 0.0_real64]
   end subroutine rhs
   subroutine jacobian(n, t, y, jac)
      integer, intent(in) :: n
      real(real64), intent(in) :: t, y(n)
      real(real64), intent(out) :: jac(n,n)
      jac = 0.0_real64
      jac(1,1) = -y(2)
      jac(1,2) = -y(1)
   end subroutine jacobian
end module decay_problem

program main
   use decay_problem
   use erk_tlm_f90_integrator, only: integrate_tlm
   implicit none
   real(real64) :: y(2), tangent(2,1), atol(2), rtol(2), atol_tlm(2,1), rtol_tlm(2,1)
   real(real64) :: exact
   integer :: status, controls(20)
   y = [1.0_real64, 2.0_real64]
   tangent(:,1) = [0.0_real64, 1.0_real64]
   atol = 1.0e-11_real64
   rtol = 1.0e-9_real64
   atol_tlm = 1.0e-11_real64
   rtol_tlm = 1.0e-9_real64
   controls = 0
   controls(5) = 1 ! Use the supplied analytical Jacobian.
   controls(12) = 1 ! Include tangent variables in adaptive error control.
   call integrate_tlm(0.0_real64, 1.0_real64, 2, 1, y, tangent, atol_tlm, &
      rtol_tlm, atol, rtol, rhs, jacobian, icntrl_u=controls, ierr_u=status)
   exact = exp(-2.0_real64)
   print '(a,f14.10)', 'y(1), exact exp(-2): ', y(1)
   print '(a,f14.10)', 'dy(1)/dk, exact -exp(-2): ', tangent(1,1)
   if (status < 0) error stop 'FATODE integration failed'
   if (abs(y(1)-exact) > 1.0e-7_real64) error stop 'Incorrect solution'
   if (abs(tangent(1,1)+exact) > 1.0e-7_real64) error stop 'Incorrect sensitivity'
   if (abs(y(2)-2.0_real64) > 1.0e-12_real64) error stop 'Constant rate changed'
   if (abs(tangent(2,1)-1.0_real64) > 1.0e-12_real64) error stop 'Rate sensitivity changed'
   print '(a)', 'PASS fatode'
end program main
