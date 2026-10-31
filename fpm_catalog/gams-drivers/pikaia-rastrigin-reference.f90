! Original G2i API driver. MIT: licenses/optimization-api-drivers-MIT.txt.
module global_problem
   use iso_fortran_env, only: wp=>real64
   use pikaia_module, only: pikaia_class
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer :: evaluations=0
contains
   function rastrigin(x) result(value)
      real(wp),intent(in) :: x(:)
      real(wp) :: value
      value=sum(x*x+10*(1-cos(2*acos(-1._wp)*x)))
   end function
   subroutine fitness(me,x,value)
      class(pikaia_class),intent(inout) :: me
      real(wp),intent(in) :: x(:)
      real(wp),intent(out) :: value
      if(.not.all(ieee_is_finite(x))) error stop 'nonfinite genetic callback'
      if(any(abs(x)>2+1.e-12_wp)) error stop 'genetic callback outside bounds'
      value=1/(1+rastrigin(x)) ! PIKAIA maximizes fitness, so the known maximum is 1 at x=0.
      evaluations=evaluations+1
   end subroutine
end module
program main
   use global_problem
   implicit none
   integer,parameter :: seeds(*)=[12345,6789,24680]
   integer :: i
   do i=1,size(seeds)
      call run(seeds(i))
   end do
   print '(a)', 'These fixed-seed finite searches do not guarantee global convergence on other problems.'
   print '(a)', 'PASS pikaia-rastrigin-reference'
contains
   subroutine run(seed)
      integer,intent(in) :: seed
      type(pikaia_class) :: solver
      real(wp) :: x(2),value,objective,reference_fitness
      integer :: status
      x=[.37_wp,-.61_wp]
      evaluations=0
      call solver%init(2,[-2._wp,-2._wp],[2._wp,2._wp],fitness,status, &
         ngen=600,np=100,nd=7,ivrb=0,iseed=seed,convergence_tol=1.e-10_wp,convergence_window=601)
      if(status/=0) error stop 'PIKAIA initialization'
      call solver%solve(x,value,status)
      if(status/=0) error stop 'PIKAIA solve status'
      if(.not.all(ieee_is_finite(x)) .or. .not.ieee_is_finite(value)) error stop 'nonfinite global result'
      if(any(abs(x)>2+1.e-12_wp)) error stop 'global result outside bounds'
      objective=rastrigin(x)
      reference_fitness=1/(1+objective)
      if(abs(value-reference_fitness)>1.e-10_wp) error stop 'reported fitness'
      if(maxval(abs(x))>1.e-2_wp .or. objective>1.e-2_wp) error stop 'known global optimum'
      print '(a,i0,a,2f14.9,a,es12.3,a,i0)', 'Seed ',seed,': x=',x,'; objective=',objective, &
         '; evaluations=',evaluations
   end subroutine
end program
