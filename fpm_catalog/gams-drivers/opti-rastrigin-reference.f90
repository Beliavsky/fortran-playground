! Independent API consumer; see licenses/gradient-swarm-drivers-MIT.txt.
module shifted_rastrigin_problem
   use iso_fortran_env, only: real64
   implicit none
   real(real64), allocatable :: center(:)
   real(real64) :: amplitude
   integer :: evaluations=0
contains
   function objective(x,n) result(f)
      integer, intent(in) :: n
      real(real64), intent(in) :: x(n)
      real(real64) :: f,d
      integer :: i
      f=0
      do i=1,n
         d=x(i)-center(i)
         f=f+d*d+amplitude*(1-cos(2*acos(-1.0_real64)*d))
      end do
      evaluations=evaluations+1
   end function objective
end module shifted_rastrigin_problem

program checked_particle_swarm
   use shifted_rastrigin_problem
   use psomod, only: optimizer
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer, parameter :: sizes(2)=[2,3],seeds(3)=[314159,271828,161803]
   real(real64), parameter :: amplitudes(2)=[1.0_real64,10.0_real64]
   real(real64), allocatable :: lower(:),upper(:),x(:)
   integer, allocatable :: seed(:)
   real(real64) :: value,reference,distance,worst_objective=0,worst_distance=0
   integer :: n,s,a,seed_id,seed_size,i,cases=0,entries=0,total_evaluations=0
   call random_seed(size=seed_size)
   allocate(seed(seed_size))
   do s=1,2
      n=sizes(s)
      allocate(center(n),lower(n),upper(n),x(n))
      center=[(real(i-2,real64)/4,i=1,n)]
      lower=center-3; upper=center+3
      do a=1,2
         amplitude=amplitudes(a)
         do seed_id=1,3
            seed=[(seeds(seed_id)+37*i,i=1,seed_size)]
            call random_seed(put=seed)
            x=huge(1.0_real64); evaluations=0
            call optimizer(80,1200,n,lower,upper,1e-10_real64,objective,x,topo=2)
            if (.not.all(ieee_is_finite(x))) error stop 'nonfinite swarm result'
            if (any(x<lower).or.any(x>upper)) error stop 'swarm result outside bounds'
            if (evaluations<1.or.evaluations>2*80*(1200+2)) error stop 'swarm evaluation budget'
            total_evaluations=total_evaluations+evaluations
            ! Independent identity: 1-cos(2*pi*d) = 2*sin(pi*d)**2.
            reference=sum((x-center)**2+2*amplitude*sin(acos(-1.0_real64)*(x-center))**2)
            value=objective(x,n); distance=maxval(abs(x-center))
            if (.not.ieee_is_finite(value).or..not.ieee_is_finite(reference)) error stop 'nonfinite swarm objective'
            if (abs(value-reference)>2e-12_real64*(1+reference)) error stop 'objective identity mismatch'
            if (reference>1e-5_real64.or.distance>1e-3_real64) then
               print *, 'Swarm fixture: ',n,amplitude,seeds(seed_id),reference,distance
               error stop 'known global Rastrigin minimum'
            end if
            worst_objective=max(worst_objective,reference); worst_distance=max(worst_distance,distance)
            cases=cases+1; entries=entries+n
         end do
      end do
      deallocate(center,lower,upper,x)
   end do
   print '(a)', 'Swarm verification summary:'
   print '(a,i0)', 'Seeded shifted-Rastrigin problems: ',cases
   print '(a,i0)', 'Known global-minimizer entries: ',entries
   print '(a,i0)', 'Optimizer callback evaluations: ',total_evaluations
   print '(a,es12.4)', 'Maximum independently evaluated objective: ',worst_objective
   print '(a,es12.4)', 'Maximum coordinate error from known global optimum: ',worst_distance
   print '(a)', 'These seeded successes do not guarantee global convergence or portability of the RNG sequence.'
   print '(a)', 'PASS opti-rastrigin-reference'
end program checked_particle_swarm
