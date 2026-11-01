! Independent MIT consumer; see licenses/pareto-diis-drivers-MIT.txt.
module pareto_quadratics
   use vtmop_lib, only: r8
   implicit none
   real(r8), allocatable :: center_a(:),center_b(:)
   integer :: evaluations=0
contains
   subroutine objectives(x,f,status)
      real(r8), intent(in) :: x(:)
      real(r8), intent(out) :: f(:)
      integer, intent(out) :: status
      f(1)=sum((x-center_a)**2); f(2)=sum((x-center_b)**2)
      evaluations=evaluations+1; status=0
   end subroutine
end module

program pareto_reference
   use pareto_quadratics
   use vtmop_lib, only: vtmop_solve,gps,lshep_fit,lshep_eval
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer, parameter :: seed_values(*)=[1729,2903]
   real(r8), allocatable :: x(:,:),f(:,:),lb(:),ub(:),projection(:),direction(:)
   integer, allocatable :: seed(:)
   real(r8) :: actual(2),d2,t,clamped,distance,best,worst,min_t,max_t,min_span,max_best,max_distance
   real(r8) :: delta_a,delta_b,gap,max_identity_error,identity_error
   integer :: n,seed_case,count,status,i,j,runs,returned,total_evaluations
   runs=0; returned=0; total_evaluations=0; min_span=huge(1._r8)
   max_best=0; max_distance=0; max_identity_error=0
   call random_seed(size=count); allocate(seed(count))
   do n=2,3
      allocate(center_a(n),center_b(n),lb(n),ub(n),projection(n),direction(n))
      center_a=[(real(i+1,r8)/10,i=1,n)]
      center_b=1-center_a
      direction=center_b-center_a; d2=sum(direction**2); lb=0; ub=1
      do seed_case=1,size(seed_values)
         seed=seed_values(seed_case); call random_seed(put=seed); evaluations=0
         call vtmop_solve(n,2,lb,ub,objectives,x,f,status,bb_budget=200,maxiters=40, &
            search_budget=6,initial_sbudget=10,lopt_budget=200,local_opt=gps, &
            fit_surrogates=lshep_fit,eval_surrogates=lshep_eval,pflag=0)
         if (status<0 .or. status>=10) error stop 'VTMOP reported failure'
         if (.not.allocated(x) .or. .not.allocated(f)) error stop 'VTMOP missing archive'
         if (size(x,1)/=n .or. size(f,1)/=2 .or. size(x,2)/=size(f,2)) error stop 'VTMOP archive shape'
         if (size(f,2)<2 .or. evaluations<=0) error stop 'VTMOP empty search'
         if (.not.all(ieee_is_finite(x)) .or. .not.all(ieee_is_finite(f))) error stop 'nonfinite VTMOP archive'
         if (any(x<lb(1)) .or. any(x>ub(1))) error stop 'VTMOP infeasible point'
         best=huge(1._r8); worst=0; min_t=huge(1._r8); max_t=-huge(1._r8)
         do i=1,size(f,2)
            ! Independent scalar objective recomputation (not the callback).
            actual=0
            do j=1,n
               actual(1)=actual(1)+(x(j,i)-center_a(j))**2
               actual(2)=actual(2)+(x(j,i)-center_b(j))**2
            end do
            if (maxval(abs(actual-f(:,i)))>1.e-12_r8) error stop 'VTMOP reported objectives differ'
            do j=1,size(f,2)
               if (all(f(:,j)<=f(:,i)) .and. any(f(:,j)<f(:,i)-1.e-10_r8)) &
                  error stop 'VTMOP archive contains dominated point'
            end do
            t=dot_product(x(:,i)-center_a,direction)/d2
            clamped=max(0._r8,min(1._r8,t)); projection=center_a+clamped*direction
            distance=sqrt(sum((x(:,i)-projection)**2))/sqrt(d2)
            best=min(best,distance); worst=max(worst,distance)
            min_t=min(min_t,clamped); max_t=max(max_t,clamped)
            ! Orthogonal projection onto the Pareto segment improves BOTH quadratics.
            delta_a=actual(1)-sum((projection-center_a)**2)
            delta_b=actual(2)-sum((projection-center_b)**2)
            gap=sum((x(:,i)-projection)**2)
            if (min(delta_a,delta_b)<-1.e-12_r8) error stop 'Pareto projection dominance identity'
            if (t>=0 .and. t<=1) then
               identity_error=max(abs(delta_a-gap),abs(delta_b-gap))
               if (identity_error>1.e-12_r8) error stop 'Pareto orthogonal-distance identity'
               max_identity_error=max(max_identity_error,identity_error)
            end if
         end do
         ! Modest predeclared accuracy/coverage thresholds for a finite evaluation budget.
         if (best>0.05_r8 .or. worst>0.15_r8) error stop 'VTMOP Pareto-segment distance'
         if (max_t-min_t<0.25_r8) error stop 'VTMOP insufficient Pareto-segment spread'
         print '(a,i0,a,i0,a,i0,a,3f11.6)', 'n=',n,' seed=',seed_values(seed_case), &
            ' archive=',size(f,2),' best/worst relative distance and span: ',best,worst,max_t-min_t
         min_span=min(min_span,max_t-min_t); max_best=max(max_best,best); max_distance=max(max_distance,worst)
         runs=runs+1; returned=returned+size(f,2); total_evaluations=total_evaluations+evaluations
      end do
      deallocate(center_a,center_b,lb,ub,projection,direction)
   end do
   if (runs/=4) error stop 'VTMOP reference run count'
   print '(a,i0,a,i0)', 'Seeded Pareto searches: ',runs,'; returned points checked: ',returned
   print '(a,i0)', 'Objective callback evaluations: ',total_evaluations
   print '(a,3es14.5)', 'Worst best-distance, worst all-point distance and minimum span: ',max_best,max_distance,min_span
   print '(a,es14.5)', 'Maximum Pareto projection identity error: ',max_identity_error
   print '(a)', 'Fixed small quadratic searches only; finite-budget accuracy, not a general convergence guarantee.'
   print '(a)', 'PASS vtmop-pareto-reference'
end program
