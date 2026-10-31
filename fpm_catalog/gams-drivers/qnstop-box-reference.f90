! Independent API consumer; MIT: licenses/matrix-roots-box-drivers-MIT.txt.
module box_reference_problem
   use qnstops_mod, only: r8
   implicit none
   real(r8) :: center(3),weights(3)
contains
   function objective(x,iflag) result(f)
      real(r8), intent(in) :: x(:)
      integer, intent(out) :: iflag
      real(r8) :: f
      f = sum(weights(:size(x))*(x-center(:size(x)))**2)
      iflag = 0
   end function objective
end module box_reference_problem

program box_reference
   use box_reference_problem
   use qnstops_mod, only: qnstops
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer, allocatable :: seed(:)
   real(r8), allocatable :: x(:),expected(:),lower(:),upper(:)
   real(r8) :: minimum,reference,optimum,error,gap,max_error,max_gap
   integer :: fixture,n,seed_size,i,status,iterations,evaluations,runs
   call random_seed(size=seed_size)
   allocate(seed(seed_size))
   runs = 0
   max_error = 0._r8
   max_gap = 0._r8
   do fixture = 1,4
      n = 2
      if (fixture == 4) n = 3
      allocate(x(n),expected(n),lower(n),upper(n))
      lower = -2._r8
      upper = 2._r8
      weights = [1._r8,2._r8,3._r8]
      center = [.25_r8,-.5_r8,0._r8]
      select case(fixture)
      case(1)
         x = [-1.5_r8,1.5_r8]
      case(2)
         x = [1.5_r8,1._r8]
      case(3)
         x = 0._r8
      case(4)
         center = [-.5_r8,0._r8,.75_r8]
         x = [1._r8,1._r8,-1._r8]
      end select
      expected = max(lower,min(upper,center(:n)))
      optimum = sum(weights(:n)*(expected-center(:n))**2)
      seed = 1728+fixture
      call random_seed(put=seed)
      iterations = 500
      evaluations = 0
      call qnstops(n,lower,upper,objective,x,'G',minimum,status,n=32,max_iter=iterations, &
         max_eval=evaluations,tau=1._r8,gain=10._r8)
      if (status < 1 .or. status > 3) error stop 'QNSTOP stopping status'
      if (.not. all(ieee_is_finite(x)) .or. .not. ieee_is_finite(minimum)) error stop 'nonfinite box result'
      if (any(x < lower) .or. any(x > upper)) error stop 'box feasibility'
      reference = 0._r8
      do i = 1,n
         reference = reference+weights(i)*(x(i)-center(i))*(x(i)-center(i))
      end do
      if (abs(minimum-reference) > 1.e-10_r8*max(1._r8,reference)) error stop 'returned objective consistency'
      error = maxval(abs(x-expected))
      gap = (minimum-optimum)/max(1._r8,optimum)
      print '(a,i0,a,i0,a,es12.4,a,es12.4)', 'Fixture=',fixture,' status=',status,' position error=',error,' gap=',gap
      if (error > .03_r8 .or. gap < -1.e-10_r8 .or. gap > .1_r8) error stop 'projected box minimum'
      if (optimum == 0 .and. minimum > 1.e-3_r8) error stop 'interior quadratic minimum'
      if (evaluations <= 0) error stop 'missing function evaluation count'
      max_error = max(max_error,error)
      max_gap = max(max_gap,gap)
      runs = runs+1
      deallocate(x,expected,lower,upper)
   end do
   if (runs /= 4) error stop 'box fixture count'
   print '(a)', 'Four seeded box-constrained quadratics with interior minima; active bounds are not verified.'
   print '(a,es12.4)', 'Maximum coordinate error versus projected minimizer: ',max_error
   print '(a,es12.4)', 'Maximum normalized objective gap: ',max_gap
   print '(a)', 'PASS qnstop-box-reference'
end program box_reference
