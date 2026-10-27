module example_functions
   use iso_fortran_env, only: wp => real64
   implicit none
contains
   subroutine objective(n,x,f)
      integer, intent(in) :: n
      real(wp), intent(in) :: x(:)
      real(wp), intent(out) :: f
      f = (x(1)-1.0_wp)**2+2*(x(2)+2.0_wp)**2
   end subroutine objective
end module example_functions

program main
   use example_functions, only: objective, wp
   use bobyqa_module, only: bobyqa
   implicit none
   real(wp) :: x(2)
   x = 0.0_wp
   call bobyqa(2,5,x,[-5.0_wp,-5.0_wp],[5.0_wp,5.0_wp],0.5_wp,1.e-8_wp,0,1000,objective)
   if (maxval(abs(x-[1.0_wp,-2.0_wp])) > 1.e-6_wp) error stop 'incorrect BOBYQA result'
   print *, 'Derivative-free minimum at:', x
   print *, 'PASS powellopt'
end program main
