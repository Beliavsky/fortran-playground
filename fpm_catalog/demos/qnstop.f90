! Serial QNSTOP: a seeded search for the minimum of a bounded quadratic.
module playground_objective
   use qnstops_mod, only: r8
   implicit none
contains
   function objective(x, iflag) result(f)
      real(r8), intent(in) :: x(:)
      integer, intent(out) :: iflag
      real(r8) :: f
      f = sum((x - [0.25_r8, -0.5_r8])**2)
      iflag = 0
   end function objective
end module playground_objective

program main
   use qnstops_mod, only: qnstops, r8
   use playground_objective, only: objective
   implicit none
   integer :: status, iterations, evaluations, count
   integer, allocatable :: seed(:)
   real(r8) :: x(2), minimum
   call random_seed(size=count)
   allocate(seed(count))
   seed = 1729
   call random_seed(put=seed)
   x = [1.5_r8, 1.0_r8]
   iterations = 500
   evaluations = 0
   call qnstops(2, [-2.0_r8, -2.0_r8], [2.0_r8, 2.0_r8], objective, &
      x, 'G', minimum, status, n=32, max_iter=iterations, max_eval=evaluations, &
      tau=1.0_r8, gain=10.0_r8)
   print '(a,2f12.7)', 'Estimated minimizer: ', x
   print '(a,es12.4)', 'Objective (exact minimum = 0): ', minimum
   print '(a,i0)', 'Stopping status: ', status
   if (status < 1 .or. status > 3) error stop 'QNSTOP did not return normally'
   if (any(x < -2.0_r8) .or. any(x > 2.0_r8)) error stop 'Outside bounds'
   if (minimum > 1.0e-4_r8 .or. maxval(abs(x-[0.25_r8,-0.5_r8])) > 0.02_r8) &
      error stop 'Known minimum was not recovered'
   print '(a)', 'PASS qnstop'
end program main
