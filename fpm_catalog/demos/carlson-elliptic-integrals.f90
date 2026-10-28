! Pendulum period beyond the small-angle approximation, using Carlson RF.
program demo_carlson
   use carlson_elliptic_module, only: wp=>carlson_elliptic_module_wp,drf
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer,parameter :: intervals=4096
   real(wp),parameter :: angles(*)=[0._wp,30._wp,90._wp,150._wp],gravity=9.80665_wp
   real(wp) :: pi,k,elliptic,reference,h,t,sum_integral,period,error
   integer :: i,j,status
   pi=acos(-1._wp)
   if (abs(drf(1._wp,1._wp,1._wp)-1._wp)>1e-13_wp) error stop 'RF identity failed'
   print '(a)', 'Amplitude (deg)  Period for L=1 m (s)   Ratio to small-angle   Quadrature error'
   do i=1,size(angles)
      k=sin(angles(i)*pi/360)
      elliptic=drf(0._wp,1-k*k,1._wp,status)
      if (status/=0) error stop 'Elliptic integral failed'
      ! Independent composite Simpson integration of the defining integral.
      h=pi/(2*intervals)
      sum_integral=1._wp+1/sqrt(1-k*k)
      do j=1,intervals-1
         t=j*h
         sum_integral=sum_integral+merge(4._wp,2._wp,mod(j,2)==1)/sqrt(1-(k*sin(t))**2)
      end do
      reference=h*sum_integral/3
      error=abs(elliptic-reference)
      if (.not.ieee_is_finite(elliptic)) error stop 'Nonfinite integral'
      if (error>1e-10_wp) error stop 'Elliptic integral differs from quadrature'
      period=4*elliptic/sqrt(gravity)
      print '(f12.1,2f23.12,es20.3)',angles(i),period,2*elliptic/pi,error
   end do
   print '(a)', 'PASS carlson-elliptic-integrals'
end program
