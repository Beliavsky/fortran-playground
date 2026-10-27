module example_functions
   use ddeabm_module, only: ddeabm_class, wp => ddeabm_rk
   implicit none
contains
   subroutine oscillator(me,t,y,dy)
      class(ddeabm_class), intent(inout) :: me
      real(wp), intent(in) :: t, y(:)
      real(wp), intent(out) :: dy(:)
      dy = [y(2),-y(1)]
   end subroutine oscillator
end module example_functions

program main
   use example_functions, only: oscillator
   use ddeabm_module, only: ddeabm_class, wp => ddeabm_rk
   implicit none
   type(ddeabm_class) :: solver
   real(wp) :: t, y(2)
   integer :: status
   t = 0.0_wp
   y = [1.0_wp,0.0_wp]
   call solver%initialize(neq=2,maxnum=10000,df=oscillator,rtol=[1.e-10_wp],atol=[1.e-10_wp])
   call solver%integrate(t,y,acos(-1.0_wp)/2,idid=status)
   if (status < 0 .or. maxval(abs(y-[0.0_wp,-1.0_wp])) > 1.e-8_wp) error stop 'incorrect oscillator result'
   print *, 'Harmonic oscillator at a quarter period:', y
   print *, 'PASS ddeabm'
end program main
