! Independent API consumer; MIT: licenses/delay-embedding-drivers-MIT.txt.
module delay_reference_problem
   implicit none
   double precision :: rate,history_value
   logical :: oscillator
contains
   subroutine rhs(t,y,z,dy)
      double precision, intent(in) :: t,y(:),z(:,:)
      double precision, intent(out) :: dy(:)
      if (oscillator) then
         dy(1) = -rate*z(1,1)
      else
         dy(1) = rate*z(1,1)
      end if
   end subroutine rhs
   subroutine history(t,y)
      double precision, intent(in) :: t
      double precision, intent(out) :: y(:)
      if (oscillator) then
         y(1) = sin(rate*t)
      else
         y(1) = history_value
      end if
   end subroutine history
end module delay_reference_problem

program delay_reference
   use delay_reference_problem
   use dde_solver_m, only: dde_set,dde_solver,dde_sol,dde_opts,dde_int,dde_val,release_arrays,release_int
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   double precision, parameter :: delays(*) = [.25d0,1.d0,2.d0],rates(*) = [.5d0,1.d0],histories(*) = [1.d0,-2.d0]
   double precision, parameter :: frequencies(*) = [.5d0,1.d0,2.d0]
   type(dde_sol) :: solution
   type(dde_opts) :: options
   type(dde_int) :: sampled
   double precision :: tau,times(65),expected(65),error,max_error,elapsed
   integer :: delay,coefficient,initial,i,runs
   runs = 0
   max_error = 0.d0
   oscillator = .false.
   do delay = 1,3
      tau = delays(delay)
      do coefficient = 1,2
         rate = rates(coefficient)
         do initial = 1,2
            history_value = histories(initial)
            times = [(real(i,8)*tau/16,i=0,64)]
            expected = history_value*(1+rate*times &
               +rate**2*max(0.d0,times-tau)**2/2 &
               +rate**3*max(0.d0,times-2*tau)**3/6 &
               +rate**4*max(0.d0,times-3*tau)**4/24)
            call solve
         end do
      end do
   end do
   oscillator = .true.
   do coefficient = 1,3
      rate = frequencies(coefficient)
      tau = acos(-1.d0)/(2*rate)
      times = [(real(i,8)*tau/16,i=0,64)]
      expected = sin(rate*times)
      call solve
   end do
   if (runs /= 15) error stop 'delay fixture count'
   print '(a)', '15 delayed solves, 975 dense-output references: method-of-steps polynomials and sinusoidal oscillators.'
   print '(a,es12.4)', 'Maximum error / max(1,abs(reference)): ',max_error
   print '(a)', 'Constant positive delays, signed history scaling, delay knots and interior samples checked.'
   print '(a)', 'PASS dde-method-steps-reference'
contains
   subroutine solve
      options = dde_set(re=1.d-10,ae=1.d-12,interpolation=.true.)
      elapsed = times(65)
      solution = dde_solver([1,1],rhs,[tau],history,[0.d0,elapsed],options=options)
      if (solution%flag /= 0) error stop 'delay solve status'
      sampled = dde_val(times,solution)
      if (any(shape(sampled%yt) /= [65,1])) error stop 'delay dense-output shape'
      if (.not. all(ieee_is_finite(sampled%yt))) error stop 'nonfinite delayed solution'
      error = maxval(abs(sampled%yt(:,1)-expected)/max(1.d0,abs(expected)))
      max_error = max(max_error,error)
      if (error > 2.d-7) error stop 'independent delayed solution'
      print '(a,l1,a,f9.5,a,f6.2,a,es12.4)', 'Oscillator=',oscillator,' delay=',tau,' rate=',rate,' error=',error
      call release_arrays(solution,options)
      call release_int(sampled)
      runs = runs+1
   end subroutine solve
end program delay_reference
