module objective_function
   implicit none
contains
   function objective(x,n) result(value)
      integer, intent(in) :: n
      real(8), intent(in) :: x(n)
      real(8) :: value
      value = sum((x-[1.0d0,-2.0d0])**2)
   end function
end module

program particle_swarm_demo
   use psomod, only: optimizer
   use objective_function, only: objective
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer, allocatable :: seed(:)
   integer :: n
   real(8) :: lower(2), upper(2), result(2), value
   call random_seed(size=n)
   allocate(seed(n),source=314159)
   call random_seed(put=seed)
   lower = -5
   upper = 5
   result = 0
   call optimizer(40,400,2,lower,upper,1.d-10,objective,result)
   value = objective(result,2)
   print '(a,2f12.6)', 'Particle swarm minimum at: ', result
   print '(a,es12.4)', 'Squared distance from (1,-2): ', value
   if (.not. ieee_is_finite(value)) error stop 'Nonfinite objective'
   if (value>1.d-5) error stop 'Optimization check'
   print *, 'PASS opti'
end program
