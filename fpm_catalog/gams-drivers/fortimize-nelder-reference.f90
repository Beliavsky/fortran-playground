! Independent API consumer; MIT: licenses/optimization-spacing-drivers-MIT.txt.
module nelder_reference_problem
   use ForTimize, only: pr
   implicit none
   type :: problem_data
      logical :: rosenbrock = .false.
      real(pr) :: center(5) = 0._pr
   end type problem_data
contains
   subroutine objective(x,f,df,data)
      real(pr), intent(in) :: x(:)
      real(pr), intent(out) :: f
      real(pr), optional, intent(out) :: df(:)
      class(*), optional, intent(inout) :: data
      real(pr) :: e(size(x)),mixed(size(x))
      integer :: i
      if (present(df)) error stop 'unexpected derivative request'
      if (.not. present(data)) error stop 'missing objective data'
      select type(data)
      type is(problem_data)
         if (data%rosenbrock) then
            f = (1-x(1))**2+100*(x(2)-x(1)**2)**2
         else
            e = x-data%center(:size(x))
            mixed = e
            mixed(:size(x)-1) = e(:size(x)-1)+.25_pr*e(2:)
            f = sum([(real(i,pr)*mixed(i)**2,i=1,size(x))])
         end if
      class default
         error stop 'objective data type'
      end select
   end subroutine objective
end module nelder_reference_problem

program nelder_reference
   use nelder_reference_problem
   use ForTimize, only: NelderMead,minimize
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer, parameter :: dimensions(*) = [2,3,5]
   type(NelderMead) :: solver
   type(problem_data), target :: data
   real(pr), allocatable :: x(:),expected(:)
   real(pr) :: f,reference,error,term,max_position_error,max_objective
   integer :: dimension,start,n,i,runs
   runs = 0
   max_position_error = 0._pr
   max_objective = 0._pr
   do dimension = 1,3
      n = dimensions(dimension)
      allocate(x(n),expected(n))
      expected = [(real((-1)**i*i,pr)/2,i=1,n)]
      data%center(:n) = expected
      data%rosenbrock = .false.
      do start = 1,3
         select case(start)
         case(1)
            x = expected-3
         case(2)
            x = expected+[(real((-1)**i*2,pr),i=1,n)]
         case(3)
            x = expected+4
         end select
         call solve
      end do
      deallocate(x,expected)
   end do
   allocate(x(2),expected(2))
   expected = 1._pr
   data%rosenbrock = .true.
   do start = 1,3
      select case(start)
      case(1)
         x = [-1.2_pr,1._pr]
      case(2)
         x = [0._pr,0._pr]
      case(3)
         x = [2._pr,2._pr]
      end select
      call solve
   end do
   if (runs /= 12) error stop 'optimization case count'
   print '(a)', '12 derivative-free solves: coupled quadratics in 2/3/5 variables and Rosenbrock, three starts each.'
   print '(a,es12.4)', 'Maximum coordinate error versus known minimizer: ',max_position_error
   print '(a,es12.4)', 'Maximum returned objective: ',max_objective
   print '(a)', 'PASS fortimize-nelder-reference'
contains
   subroutine solve
      solver%convergence_tolerance = 1.e-20_pr
      solver%konvge = 20
      solver%kcount = 50000
      solver%step = [( .4_pr,i=1,size(x))]
      call minimize(objective,x,f,solver,data=data)
      if (.not. all(ieee_is_finite(x)) .or. .not. ieee_is_finite(f)) error stop 'nonfinite optimizer output'
      if (data%rosenbrock) then
         reference = (x(2)-x(1)*x(1))**2*100+(x(1)-1)**2
      else
         reference = 0._pr
         do i = 1,size(x)
            term = x(i)-expected(i)
            if (i < size(x)) term = term+.25_pr*(x(i+1)-expected(i+1))
            reference = reference+real(i,pr)*term*term
         end do
      end if
      if (abs(f-reference) > 1.e-12_pr) error stop 'returned objective consistency'
      error = maxval(abs(x-expected))
      max_position_error = max(max_position_error,error)
      max_objective = max(max_objective,f)
      if (error > 2.e-4_pr .or. f < 0 .or. f > 1.e-8_pr) error stop 'known optimum reference'
      runs = runs+1
      print '(a,i0,a,l1,a,es12.4)', 'Variables=',size(x),' Rosenbrock=',data%rosenbrock,' coordinate error=',error
   end subroutine solve
end program nelder_reference
