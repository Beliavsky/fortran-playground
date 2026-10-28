! Intended consumer; source preparation currently rejects the upstream archive.
! Minimize (x-1)**2+(y-1)**2 with x+y>=3 and nonnegative variables.
program demo_daqp
   use daqp_module, wp=>daqp_wp
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   type(daqp_type) :: solver
   real(wp) :: h(2,2),x(2),multipliers(3),objective
   integer :: status
   h=0
   h(1,1)=2; h(2,2)=2
   call solver%setup(h,[-2._wp,-2._wp],reshape([1._wp,1._wp],[1,2]), &
      bupper=[daqp_inf,daqp_inf,daqp_inf],blower=[0._wp,0._wp,3._wp],istat=status)
   if (status/=daqp_success) error stop 'QP setup failed'
   call solver%solve(x,multipliers,status)
   if (status<=0) error stop 'QP solve failed'
   if (.not.all(ieee_is_finite(x))) error stop 'Nonfinite QP result'
   objective=sum((x-1)**2)
   if (maxval(abs(x-1.5_wp))>1e-8_wp) error stop 'Incorrect QP optimum'
   if (sum(x)<3._wp-1e-8_wp) error stop 'QP constraint violated'
   if (abs(objective-0.5_wp)>1e-8_wp) error stop 'Incorrect QP objective'
   print '(a,2f15.9)', 'Optimum: ',x
   print '(a,f15.9)', 'Objective: ',objective
   print '(a)', 'PASS daqp-fortran'
end program
