! Independent API consumer; MIT: licenses/sparse-integral-drivers-MIT.txt.
program spline_integral
   use fitpack, only: fitpack_curve, FP_REAL, FP_FLAG, FITPACK_SUCCESS
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer, parameter :: wp = FP_REAL, n = 9
   type(fitpack_curve) :: curve
   real(wp), parameter :: x(n) = [-2._wp,-1.7_wp,-1._wp,-.25_wp,0._wp,.4_wp,1._wp,1.6_wp,2._wp]
   real(wp), parameter :: bounds(2,6) = reshape([-2._wp,2._wp, -.7_wp,1.3_wp, -2._wp,-.25_wp, &
      .4_wp,2._wp, 1.3_wp,-.7_wp, .2_wp,.2_wp],[2,6])
   real(wp) :: y(n),actual,expected,left,right,total,query,value,error
   integer(FP_FLAG) :: status
   integer :: degree,i,k,checks
   checks = 0
   do degree = 0,3
      y = x**degree
      status = curve%new_fit(x,y,smoothing=0._wp)
      if (.not. FITPACK_SUCCESS(status)) error stop 'interpolating spline fit status'
      ! A cubic interpolant must reproduce these polynomials, including off-grid points.
      do i = 0,16
         query = -2._wp+real(i,wp)/4
         value = curve%eval(query,status)
         if (.not. FITPACK_SUCCESS(status)) error stop 'spline evaluation status'
         if (.not. ieee_is_finite(value)) error stop 'nonfinite spline value'
         if (abs(value-query**degree) > 1.e-11_wp) error stop 'polynomial reproduction'
      end do
      error = 0._wp
      do k = 1,size(bounds,2)
         actual = curve%integral(bounds(1,k),bounds(2,k))
         expected = primitive(bounds(2,k),degree)-primitive(bounds(1,k),degree)
         if (.not. ieee_is_finite(actual)) error stop 'nonfinite spline integral'
         error = max(error,abs(actual-expected))
         if (abs(actual-expected) > 1.e-11_wp) error stop 'analytic polynomial integral'
         checks = checks+1
      end do
      left = curve%integral(-2._wp,.15_wp)
      right = curve%integral(.15_wp,2._wp)
      total = curve%integral(-2._wp,2._wp)
      if (.not. all(ieee_is_finite([left,right,total]))) error stop 'nonfinite partition integrals'
      if (abs(left-(primitive(.15_wp,degree)-primitive(-2._wp,degree))) > 1.e-11_wp) &
         error stop 'left partition antiderivative'
      if (abs(right-(primitive(2._wp,degree)-primitive(.15_wp,degree))) > 1.e-11_wp) &
         error stop 'right partition antiderivative'
      if (abs(left+right-total) > 1.e-11_wp) error stop 'integral additivity'
      checks = checks+3
      print '(a,i0,a,es10.2)', 'Polynomial degree ',degree,' maximum integral error=',error
      call curve%destroy()
   end do
   if (checks /= 36) error stop 'integral check count'
   print '(a)', '36 integrals checked, including reversed/zero intervals and off-knot partition additivity.'
   print '(a)', 'PASS fitpack-spline-integral'
contains
   real(wp) function primitive(t,degree)
      real(wp), intent(in) :: t
      integer, intent(in) :: degree
      primitive = t**(degree+1)/real(degree+1,wp)
   end function primitive
end program spline_integral
