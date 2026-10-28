module playground_stiff3_rates
   use stiff3_solver, only: wp => stiff3_wp
   implicit none
contains
   subroutine rate(n,y,f,ires)
      integer, intent(in) :: n
      real(wp), intent(in) :: y(n)
      real(wp), intent(inout) :: f(n)
      integer, intent(inout) :: ires
      f(1) = -0.04_wp*y(1)+1e4_wp*y(2)*y(3)
      f(3) = 3e7_wp*y(2)**2
      f(2) = -f(1)-f(3)
   end subroutine
   subroutine jacobian(n,y,df)
      integer, intent(in) :: n
      real(wp), intent(in) :: y(n)
      real(wp), intent(inout) :: df(n,n)
      df(1,:) = [-0.04_wp, 1e4_wp*y(3), 1e4_wp*y(2)]
      df(3,:) = [0.0_wp, 6e7_wp*y(2), 0.0_wp]
      df(2,:) = -df(1,:)-df(3,:)
   end subroutine
end module

program demo_stiff3
   use stiff3_solver, only: stiff3, wp => stiff3_wp
   use playground_stiff3_rates, only: rate,jacobian
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   real(wp) :: y(3), weights(3), time, finish, step
   real(wp), parameter :: reference(3) = [0.183202_wp,8.94237e-7_wp,0.816797_wp]
   integer :: status, stats(6)
   y = [1.0_wp,0.0_wp,0.0_wp]
   weights = [1.0_wp,1e-4_wp,1.0_wp]
   time = 0; finish = 4000; step = 1e-6_wp
   call stiff3(3,rate,time,y,finish,jacobian,step,1e-8_wp,weights,status,stats=stats)
   if (status /= 0) error stop 'Stiff solver failed'
   if (.not. all(ieee_is_finite(y))) error stop 'Nonfinite concentrations'
   if (any(y < 0.0_wp)) error stop 'Negative concentration'
   if (abs(sum(y)-1.0_wp)>1e-7_wp) error stop 'Mass is not conserved'
   if (maxval(abs(y-reference))>3e-6_wp) error stop 'Reference concentrations differ'
   print '(a,3es16.7)', 'Robertson concentrations at t=4000:',y
   print '(a,es12.4)', 'Mass conservation error:',abs(sum(y)-1.0_wp)
   print '(a,6i8)', 'Accepted/rejected steps, RHS/Jacobian calls, LU/solves:',stats
   print '(a)', 'PASS stiff3'
end program
