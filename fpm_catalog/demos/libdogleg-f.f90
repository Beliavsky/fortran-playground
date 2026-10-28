module playground_dogleg_fit
   use iso_c_binding, only: wp => c_double
   implicit none
contains
   subroutine residual(x,f,jac,params)
      real(wp), intent(in) :: x(:)
      real(wp), intent(out) :: f(:),jac(:,:)
      class(*), intent(in), optional :: params
      real(wp) :: time,exponential,observed
      integer :: i
      do i=1,size(f)
         time = real(i-1,wp)/5
         exponential = exp(-x(2)*time)
         observed = 2.5_wp*exp(-0.7_wp*time)
         f(i) = x(1)*exponential-observed
         jac(1,i) = exponential
         jac(2,i) = -time*x(1)*exponential
      end do
   end subroutine
end module

program demo_dogleg
   use dogleg, only: dl_parameters2_t,dl_getDefaultParameters,dl_optimize
   use playground_dogleg_fit, only: wp,residual
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   type(dl_parameters2_t) :: settings
   real(wp) :: x(2),objective,f(11),jac(2,11)
   x = [1.5_wp,0.3_wp]
   call dl_getDefaultParameters(settings)
   settings%max_iterations = 100
   settings%dogleg_debug = 0
   call dl_optimize(objective,x,11,residual,parameters=settings)
   if (.not. all(ieee_is_finite(x))) error stop 'Nonfinite fitted parameters'
   call residual(x,f,jac)
   if (.not. all(ieee_is_finite(f))) error stop 'Nonfinite residuals'
   if (maxval(abs(x-[2.5_wp,0.7_wp]))>1e-6_wp) error stop 'Known fit parameters differ'
   if (norm2(f)>1e-6_wp) error stop 'Fit residual too large'
   print '(a)', 'Fit amplitude*exp(-rate*t) to eleven exact observations.'
   print '(a,2f14.8)', 'Recovered amplitude and rate: ',x
   print '(a,es12.3)', 'Independently evaluated residual norm: ',norm2(f)
   print '(a)', 'PASS libdogleg-f'
end program
