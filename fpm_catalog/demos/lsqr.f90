program main
   use lsqr_kinds, only: wp, zero
   use lsqr_module, only: lsqr_solver_ez
   implicit none
   type(lsqr_solver_ez) :: solver
   real(wp) :: x(2)
   integer :: status
   ! Sparse diagonal matrix diag(2,3), represented by its two nonzero entries.
   call solver%initialize(2,2,[2.0_wp,3.0_wp],[1,2],[1,2])
   call solver%solve([4.0_wp,9.0_wp],zero,x,status)
   if (status < 1 .or. status > 2) error stop 'solver did not converge'
   if (maxval(abs(x-[2.0_wp,3.0_wp])) > 1.e-10_wp) error stop 'incorrect solution'
   print *, 'Solution of diag(2,3)*x = (4,9):', x
   print *, 'PASS lsqr'
end program main
