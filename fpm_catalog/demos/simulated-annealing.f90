module objective_module
   use simulated_annealing_module, only: simulated_annealing_type, dp => simann_wp
   implicit none
contains
   subroutine objective(me,x,value,status)
      class(simulated_annealing_type), intent(inout) :: me
      real(dp), intent(in) :: x(:)
      real(dp), intent(out) :: value
      integer, intent(out) :: status
      ! Rastrigin function: global minimum is zero at (0,0).
      value=sum(x*x+10._dp*(1._dp-cos(2*acos(-1._dp)*x)))
      status=0
   end subroutine objective
end module objective_module
program main
   use objective_module
   use iso_fortran_env, only: output_unit
   implicit none
   type(simulated_annealing_type) :: solver
   real(dp) :: x(2), best(2), step(2), temperature, value
   integer :: accepted, evaluations, status
   x=[2.5_dp,-1.5_dp]; step=1._dp; temperature=20._dp
   call solver%initialize(objective,2,[-5._dp,-5._dp],[5._dp,5._dp],[2._dp,2._dp], &
      .false.,1.e-8_dp,20,10,4,200000,0,1,2,1,0.1_dp,output_unit)
   call solver%optimize(x,0.85_dp,temperature,step,best,value,accepted,evaluations,status)
   print *, 'Optimization status, point and value:',status,best,value
   if (status /= 0) error stop 'annealing did not converge'
   if (value > 1.e-5_dp .or. maxval(abs(best))>1.e-3_dp) error stop 'incorrect global minimum'
   print *, 'Best point:',best
   print *, 'Objective and evaluations:',value,evaluations
   print *, 'PASS simulated-annealing'
end program main
