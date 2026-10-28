module chemical_kinetics
   use odepack_mod, only: dp, lsoda_class
   implicit none
contains
   subroutine robertson(self,neq,t,y,dydt,ierr)
      class(lsoda_class), intent(inout) :: self
      integer, intent(in) :: neq
      real(dp), intent(in) :: t, y(neq)
      real(dp), intent(out) :: dydt(neq)
      integer, intent(out) :: ierr
      dydt(1) = -0.04_dp*y(1)+1.e4_dp*y(2)*y(3)
      dydt(3) = 3.e7_dp*y(2)**2
      dydt(2) = -dydt(1)-dydt(3)
      ierr = 0
   end subroutine
end module

program stiff_reactions
   use chemical_kinetics, only: dp, lsoda_class, robertson
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   type(lsoda_class) :: solver
   real(dp) :: y(3), t, tout, atol(1)
   real(dp), parameter :: targets(5) = [0.4_dp,4.0_dp,40.0_dp,400.0_dp,4000.0_dp]
   integer :: state, i
   call solver%initialize(robertson,3,istate=state)
   if (state<0) error stop 'Solver initialization'
   y = [1.0_dp,0.0_dp,0.0_dp]
   t = 0
   atol = 1.e-12_dp
   state = 1
   print '(a)', '          Time             A             B             C'
   do i=1,size(targets)
      tout = targets(i)
      call solver%integrate(y,t,tout,1.e-8_dp,atol,1,state)
      if (state<0) error stop 'Integration failed'
      if (.not. all(ieee_is_finite(y))) error stop 'Nonfinite concentration'
      if (abs(t-tout)>1.e-7_dp .or. abs(sum(y)-1)>1.e-7_dp) error stop 'Conservation check'
      if (minval(y)<-1.e-10_dp) error stop 'Negative concentration'
      print '(4es14.5)', t,y
   end do
   ! Standard Robertson reference at t=4000, independent of this solver call.
   if (maxval(abs(y-[0.183202_dp,8.94237e-7_dp,0.816797_dp]))>3.e-6_dp) error stop 'Reference check'
   print '(a)', 'Total concentration remains 1; final state agrees with the reference.'
   print *, 'PASS odepack'
end program
