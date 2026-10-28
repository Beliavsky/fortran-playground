module playground_rkf45_oscillator
   use rkf45_module, only: rk
   implicit none
contains
   subroutine oscillator(t,y,dy)
      real(rk), intent(in) :: t,y(:)
      real(rk), intent(out) :: dy(:)
      dy = [y(2),-y(1)]
   end subroutine
end module

program demo_rkf45
   use rkf45_module, only: rk,rkf45
   use playground_rkf45_oscillator, only: oscillator
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   real(rk) :: y(2),t,target,relative,absolute,work(15),error,exact(2)
   integer :: flag,iwork(5),i
   y = [1.0_rk,0.0_rk]; t = 0
   relative = 1e-9_rk; absolute = 1e-11_rk
   work = 0; iwork = 0; flag = 1
   print '(a)', 'Harmonic oscillator y''''=-y, y(0)=1, y''(0)=0'
   print '(a)', '       Time          Position          Velocity          Max error'
   do i=1,8
      target = real(i,rk)*acos(-1.0_rk)/4.0_rk
      call rkf45(oscillator,2,y,t,target,relative,absolute,flag,work,iwork)
      if (flag/=2) error stop 'RKF45 did not reach the requested time'
      exact = [cos(t),-sin(t)]
      if (.not. all(ieee_is_finite(y))) error stop 'Nonfinite oscillator state'
      error = maxval(abs(y-exact))
      if (error>1e-7_rk) error stop 'Analytic solution differs'
      print '(4f18.10)',t,y,error
   end do
   print '(a)', 'PASS rkf45'
end program
