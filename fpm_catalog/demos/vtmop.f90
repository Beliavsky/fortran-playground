! Adapted from the author's serial driver and CONVEX test function.
program main
   use vtmop_lib
   use vtmop_func_mod, only: convex
   implicit none
   integer, parameter :: dimensions = 3, objectives = 2
   real(r8), allocatable :: x(:,:), f(:,:)
   real(r8) :: actual(objectives), center(dimensions)
   integer, allocatable :: seed(:)
   integer :: count, status, i, j, k
   call random_seed(size=count)
   allocate(seed(count))
   seed = 1729
   call random_seed(put=seed)
   call vtmop_solve(dimensions, objectives, [0.0_r8,0.0_r8,0.0_r8], &
      [1.0_r8,1.0_r8,1.0_r8], convex, x, f, status, bb_budget=100, &
      maxiters=20, search_budget=6, initial_sbudget=10, lopt_budget=200, &
      local_opt=gps, fit_surrogates=lshep_fit, eval_surrogates=lshep_eval, pflag=0)
   if (status < 0 .or. status >= 10) error stop 'VTMOP failed'
   if (.not. allocated(x) .or. .not. allocated(f)) error stop 'No solutions'
   if (size(f,2) < 2) error stop 'Expected multiple trade-off points'
   if (any(x < 0.0_r8) .or. any(x > 1.0_r8)) error stop 'Infeasible point'
   do i = 1, size(f,2)
      do k = 1, objectives
         center = 0.1_r8
         center(k) = 0.6_r8
         actual(k) = sum((x(:,i)-center)**2)
      end do
      if (maxval(abs(actual-f(:,i))) > 1.0e-10_r8) error stop 'Incorrect objective values'
      do j = 1, size(f,2)
         if (all(f(:,j) <= f(:,i)) .and. any(f(:,j) < f(:,i)-1.0e-10_r8)) &
            error stop 'Dominated point in reported set'
      end do
   end do
   if (maxval(f(1,:))-minval(f(1,:)) < 1.0e-3_r8) error stop 'No trade-off spread'
   print '(a,i0)', 'Nondominated solutions found: ', size(f,2)
   print '(a)', 'First trade-off objective pairs:'
   do i = 1, min(5,size(f,2))
      print '(2f12.6)', f(:,i)
   end do
   print '(a)', 'Verified bounds, objective formulas and nondominance within the returned set.'
   print '(a)', 'PASS vtmop'
end program main
