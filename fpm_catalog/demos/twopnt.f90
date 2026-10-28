program main
   use iso_fortran_env, only: output_unit
   use ieee_arithmetic, only: ieee_is_finite
   use twopnt_core
   use twopnt_test, only: SwirlingFlow
   implicit none
   type(SwirlingFlow) :: problem
   logical :: error
   character(16) :: reason
   integer :: n
   call problem%new(error,output_unit)
   if (error) error stop 'Initialization failed'
   call problem%run(error,output_unit,reason,problem%U)
   if (error) error stop 'Boundary-value solver failed'
   n=problem%domain%points
   if (.not.all(ieee_is_finite(problem%U(:,:n)))) error stop
   if (abs(problem%U(5,1)-problem%TZERO)>1e-5_RK) error stop 'First temperature boundary failed'
   if (abs(problem%U(5,n)-problem%TMAX)>1e-5_RK) error stop 'Last temperature boundary failed'
   call problem%summary(output_unit)
   print *, 'PASS twopnt'
end program main
