module example_functions
   use pikaia_module, only: pikaia_class
   use iso_fortran_env, only: wp => real64
   implicit none
contains
   subroutine fitness(me,x,f)
      class(pikaia_class), intent(inout) :: me
      real(wp), intent(in) :: x(:)
      real(wp), intent(out) :: f
      ! Pikaia maximizes fitness. Its maximum here is at (0.3,0.7).
      f = 1.0_wp-(x(1)-0.3_wp)**2-(x(2)-0.7_wp)**2
   end subroutine fitness
end module example_functions

program main
   use example_functions, only: fitness
   use pikaia_module, only: pikaia_class
   use iso_fortran_env, only: wp => real64
   implicit none
   type(pikaia_class) :: solver
   real(wp) :: x(2), f
   integer :: status
   x = 0.5_wp
   call solver%init(2,[0.0_wp,0.0_wp],[1.0_wp,1.0_wp],fitness,status, &
      ngen=300,np=100,nd=6,ivrb=0,iseed=12345)
   if (status /= 0) error stop 'initialization failed'
   call solver%solve(x,f,status)
   if (status /= 0 .or. maxval(abs(x-[0.3_wp,0.7_wp])) > 0.01_wp) error stop 'incorrect optimum'
   print *, 'Genetic algorithm optimum:', x, 'fitness:', f
   print *, 'PASS pikaia'
end program main
