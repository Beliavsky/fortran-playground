! Adapted from the author's delay_oscillator test: y'(t)=-y(t-pi/2), history sin(t).
! The exact solution remains sin(t). Keep callbacks in a module.
module playground_delay_callbacks
   implicit none
contains
   subroutine rhs(t,y,z,dy)
      double precision, intent(in) :: t,y(:),z(:,:)
      double precision, intent(out) :: dy(:)
      dy(1) = -z(1,1)
   end subroutine
   subroutine history(t,y)
      double precision, intent(in) :: t
      double precision, intent(out) :: y(:)
      y(1) = sin(t)
   end subroutine
end module
program demo_dde_solver
   use playground_delay_callbacks
   use dde_solver_m, only: dde_set, dde_solver, dde_sol, dde_opts, dde_int, &
      dde_val, release_arrays, release_int
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   type(dde_sol) :: sol
   type(dde_opts) :: opts
   type(dde_int) :: sampled
   double precision :: pi, times(9), err
   integer :: i
   pi = acos(-1d0)
   opts = dde_set(re=1d-9,ae=1d-12,interpolation=.true.)
   sol = dde_solver([1,1],rhs,[pi/2],history,[0d0,2*pi],options=opts)
   if (sol%flag/=0) error stop 'Delay solver failed'
   times = [(real(i,kind(pi))*pi/4,i=0,8)]
   sampled = dde_val(times,sol)
   if (.not. all(ieee_is_finite(sampled%yt))) error stop 'Nonfinite delay solution'
   err = maxval(abs(sampled%yt(:,1)-sin(times)))
   print '(a)', 'Time             Numerical y          Exact y'
   do i=1,size(times)
      print '(3f20.10)', times(i),sampled%yt(i,1),sin(times(i))
   end do
   print '(a,es12.3)', 'Maximum error: ',err
   if (err>1d-7) error stop 'Delay solution inaccurate'
   call release_arrays(sol,opts)
   call release_int(sampled)
   print '(a)', 'PASS dde_solver'
end program
