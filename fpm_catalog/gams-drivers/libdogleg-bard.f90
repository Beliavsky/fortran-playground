! Adapted from ivan-pi/libdogleg-f example/lmder_example.f90 at
! 32b65ae4f880a052768c05d24c24b79920710681.
! SPDX-License-Identifier: LGPL-3.0-or-later
! This adapted example is distributed under LGPL version 3 or later,
! without any warranty. See licenses/libdogleg-COPYING.LESSER and
! licenses/libdogleg-COPYING, or https://www.gnu.org/licenses/.
! Changes: common Bard-15 reference checks and suppressed debug logging.
module bard_problem
   use iso_c_binding, only: wp => c_double
   implicit none
   real(wp), parameter :: observations(15) = [ &
      .14_wp,.18_wp,.22_wp,.25_wp,.29_wp,.32_wp,.35_wp,.39_wp, &
      .37_wp,.58_wp,.73_wp,.96_wp,1.34_wp,2.10_wp,4.39_wp]
   real(wp), parameter :: expected(3) = [.08241058_wp,1.133037_wp,2.343695_wp]
   real(wp), parameter :: expected_norm = .09063596_wp
   integer :: calls = 0
contains
   subroutine evaluate(x,residual)
      real(wp), intent(in) :: x(3)
      real(wp), intent(out) :: residual(15)
      integer :: i
      do i=1,15
         residual(i) = observations(i) - (x(1)+real(i,wp)/ &
            (x(2)*real(16-i,wp)+x(3)*real(min(i,16-i),wp)))
      end do
   end subroutine

   subroutine callback(x,residual,jacobian,params)
      real(wp), intent(in) :: x(:)
      real(wp), intent(out) :: residual(:),jacobian(:,:)
      class(*), optional, intent(in) :: params
      real(wp) :: denominator,u,v,w
      integer :: i
      calls = calls + 1
      call evaluate(x,residual)
      do i=1,15
         u=real(i,wp); v=real(16-i,wp); w=real(min(i,16-i),wp)
         denominator=(x(2)*v+x(3)*w)**2
         jacobian(1,i)=-1.0_wp
         jacobian(2,i)=u*v/denominator
         jacobian(3,i)=u*w/denominator
      end do
   end subroutine
end module

program gams_libdogleg_bard
   use dogleg, only: dl_parameters2_t,dl_getDefaultParameters,dl_optimize
   use bard_problem
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   type(dl_parameters2_t) :: settings
   real(wp) :: x(3),objective,residual(15),residual_norm,parameter_error
   x = [1.0_wp,1.0_wp,1.0_wp]
   call dl_getDefaultParameters(settings)
   settings%max_iterations=200
   settings%dogleg_debug=0
   settings%Jt_x_threshold=sqrt(epsilon(1.0_wp))
   settings%update_threshold=sqrt(epsilon(1.0_wp))
   settings%trustregion_threshold=sqrt(epsilon(1.0_wp))
   call dl_optimize(objective,x,15,callback,parameters=settings)
   call evaluate(x,residual)
   residual_norm = norm2(residual)
   parameter_error = maxval(abs(x-expected))
   if (.not. all(ieee_is_finite(x)) .or. .not. ieee_is_finite(residual_norm)) error stop 'Nonfinite fit'
   if (parameter_error>2.0e-4_wp) error stop 'Reference parameters differ'
   if (abs(residual_norm-expected_norm)>1.0e-7_wp) error stop 'Reference residual norm differs'
   print '(a)', 'GAMS G1b: Bard-15 nonlinear least squares, libdogleg-f.'
   print '(a,3f14.8)', 'Parameters: ',x
   print '(a,es12.3)', 'Maximum parameter error: ',parameter_error
   print '(a,es16.8)', 'Independent residual norm: ',residual_norm
   print '(a,i0)', 'Residual and analytic Jacobian callback calls: ',calls
   print '(a)', 'PASS libdogleg-bard'
end program
