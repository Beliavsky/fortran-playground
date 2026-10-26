program main
   use bspline_module, only: bspline_1d
   use bspline_kinds_module, only: wp, ip
   implicit none
   type(bspline_1d) :: spline
   integer(ip) :: status
   real(wp) :: value
   call spline%initialize([0.0_wp,1.0_wp,2.0_wp], [0.0_wp,2.0_wp,4.0_wp], 2_ip, status)
   if (status /= 0) error stop 'initialization failed'
   call spline%evaluate(0.5_wp, 0_ip, value, status)
   if (status /= 0 .or. abs(value-1.0_wp) > 1.e-10_wp) error stop 'incorrect spline'
   print *, 'Interpolated value:', value
   call spline%destroy()
   print *, 'PASS bspline-fortran'
end program main
