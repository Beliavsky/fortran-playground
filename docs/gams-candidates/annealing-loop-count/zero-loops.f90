! Independent MIT-licensed driver; see licenses/directions-fitting-drivers-MIT.txt.
module annealing_fixture
   use simulated_annealing_module, only: simulated_annealing_type,wp => simann_wp
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   real(wp), allocatable :: center(:)
   real(wp) :: amplitude
   integer :: callback_calls
contains
   subroutine objective(me,x,f,status)
      class(simulated_annealing_type), intent(inout) :: me
      real(wp), intent(in) :: x(:)
      real(wp), intent(out) :: f
      integer, intent(out) :: status
      real(wp) :: y(size(x)),pi
      if (.not.all(ieee_is_finite(x))) error stop 'nonfinite trial point'
      if (any(abs(x-center)>3.0_wp)) error stop 'trial outside declared bounds'
      callback_calls=callback_calls+1
      y=x-center; pi=acos(-1.0_wp)
      f=sum(y*y+amplitude*(1-cos(2*pi*y)))
      if (.not.ieee_is_finite(f)) error stop 'nonfinite objective'
      status=0
   end subroutine
end module

program reference_annealing
   use annealing_fixture
   use, intrinsic :: iso_fortran_env, only: output_unit
   implicit none
   integer, parameter :: seeds(2,3)=reshape([1,2,1234,5678,91,2718],[2,3])
   type(simulated_annealing_type) :: solver
   real(wp), allocatable :: x(:),best(:),step(:)
   real(wp) :: temperature,value,reference_value,point_error,identity,max_value,max_point,max_identity
   integer :: n,amp,sd,i,accepted,evaluations,status,runs,entries,total_evaluations
   runs=0; entries=0; total_evaluations=0
   max_value=0; max_point=0; max_identity=0
   do n=2,3
      allocate(center(n),x(n),best(n),step(n))
      center=[(real(i-2,wp)/4,i=1,n)]
      do amp=1,10,9
         amplitude=real(amp,wp)
         do sd=1,size(seeds,2)
            x=center+[(2.5_wp*(-1.0_wp)**i,i=1,n)]
            step=1; temperature=20; callback_calls=0
            call solver%initialize(objective,n,center-3,center+3,maximize=.false.,eps=1e-9_wp, &
               ns=20,nt=10,neps=4,maxevl=300000,iprint=0,iseed1=seeds(1,sd),iseed2=seeds(2,sd), &
               step_mode=1,iunit=output_unit,use_initial_guess=.true.,n_resets=0,optimal_f_specified=.false.)
            call solver%optimize(x,0.85_wp,temperature,step,best,value,accepted,evaluations,status)
            if (.not.all(ieee_is_finite(best)) .or. .not.ieee_is_finite(value)) error stop 'nonfinite best point'
            ! Independent nonnegative identity: z**2+A*(1-cos(2*pi*z)) = z**2+2*A*sin(pi*z)**2.
            reference_value=sum((best-center)**2+2*amplitude*sin(acos(-1.0_wp)*(best-center))**2)
            point_error=maxval(abs(best-center))
            identity=abs(reference_value-value)/(1+reference_value)
            print '(a,4i9,3es14.5)', 'Case dimension, amplitude, seed pair, objective/point/identity: ', &
               n,amp,seeds(:,sd),reference_value,point_error,identity
            if (status/=0) error stop 'annealing did not meet its termination criteria'
            if (evaluations/=callback_calls .or. evaluations>300000) error stop 'callback count/budget mismatch'
            if (accepted<0 .or. accepted>evaluations) error stop 'invalid acceptance count'
            if (any(abs(best-center)>3.0_wp)) error stop 'returned point outside bounds'
            if (reference_value>1e-5_wp .or. point_error>1e-3_wp) error stop 'known global minimum differs'
            if (identity>2e-12_wp) error stop 'returned objective disagrees with independent identity'
            max_value=max(max_value,reference_value); max_point=max(max_point,point_error)
            max_identity=max(max_identity,identity); total_evaluations=total_evaluations+evaluations
            runs=runs+1; entries=entries+n
            call solver%destroy()
         end do
      end do
      deallocate(center,x,best,step)
   end do
   print '(a,i0,a,i0)', 'Seeded annealing runs: ',runs,'; global minimizer coordinates: ',entries
   print '(a,i0)', 'Independently counted objective callbacks: ',total_evaluations
   print '(a,3es14.5)', 'Max independent objective, point error, objective identity error: ', &
      max_value,max_point,max_identity
   print '(a)', 'PASS annealing-rastrigin-reference'
end program
