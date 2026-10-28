! Maximize -y subject to x+y >= 2 and x-y <= 4.
! Their intersection gives the independently known optimum (3,-1).
program demo_conmax
   use conmax_module, only: slnpro
   use iso_fortran_env, only: real64
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   real(real64) :: v(7,4), x(3), y(6)
   integer :: iyrct(6), ixrct(6), iycct(3), indic

   v = 0; x = 0; y = 0
   iyrct = 0; ixrct = 0; iycct = 0
   v(1,1:3) = [-1.0_real64,-1.0_real64,-2.0_real64]
   v(2,1:3) = [ 1.0_real64,-1.0_real64, 4.0_real64]
   v(3,1:2) = [ 0.0_real64, 1.0_real64]
   iyrct(1) = -1
   call slnpro(v,2,2,iyrct,y,ixrct,iycct,2,2,x,indic)
   if (indic /= 0) error stop 'Solver did not report success'
   if (.not. all(ieee_is_finite(x(:2)))) error stop 'Nonfinite solution'
   if (maxval(abs(x(:2)-[3.0_real64,-1.0_real64])) > 1e-9_real64) error stop 'Wrong optimum'
   if (x(1)+x(2) < 2.0_real64-1e-9_real64) error stop 'First constraint violated'
   if (x(1)-x(2) > 4.0_real64+1e-9_real64) error stop 'Second constraint violated'
   print '(a,2f12.6)', 'Optimal x,y: ',x(:2)
   print '(a,f12.6)', 'Maximum -y: ',-x(2)
   print '(a)', 'PASS conmax'
end program
