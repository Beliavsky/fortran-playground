module example_functions
   use dvode_module, only: dvode_t
   use dvode_kinds_module, only: wp => dvode_wp
   implicit none
contains
   subroutine stiff_decay(me,n,t,y,dy)
      class(dvode_t), intent(inout) :: me
      integer :: n
      real(wp) :: t, y(n), dy(n)
      ! Exact solution cos(t); the -1000*(y-cos(t)) term makes the equation stiff.
      dy = -1000.0_wp*(y-cos(t))-sin(t)
   end subroutine stiff_decay
end module example_functions

program main
   use example_functions, only: stiff_decay
   use dvode_module, only: dvode_t
   use dvode_kinds_module, only: wp => dvode_wp
   implicit none
   type(dvode_t) :: solver
   real(wp) :: t, y(1), work(100)
   integer :: iwork(40), status
   t = 0.0_wp
   y = 1.0_wp
   work = 0.0_wp
   iwork = 0
   status = 1
   call solver%initialize(f=stiff_decay)
   ! MF=22: BDF method with an internally approximated full Jacobian.
   call solver%solve(1,y,t,1.0_wp,1,[1.e-8_wp],[1.e-10_wp],1,status,0,work,100,iwork,40,22)
   if (status < 0 .or. abs(y(1)-cos(1.0_wp)) > 1.e-6_wp) error stop 'incorrect stiff solution'
   print *, 'Stiff equation at t=1:', y, 'exact:', cos(1.0_wp)
   print *, 'PASS dvode'
end program main
