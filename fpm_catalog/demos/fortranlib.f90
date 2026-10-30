program main
   use, intrinsic :: iso_fortran_env, only: real64
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   use lib_algebra, only: quadratic
   use lib_array, only: linspace, integral, interp1d, ipos, xval
   implicit none
   real(real64) :: x(101), y(101), roots(2), area, midpoint

   call linspace(0.0_real64, 1.0_real64, x)
   y = 2*x+1
   area = integral(x, y)
   midpoint = interp1d(x, y, 0.375_real64)
   call quadratic(1.0_real64, -5.0_real64, 6.0_real64, roots(1), roots(2))
   if (.not. all(ieee_is_finite([area, midpoint, roots]))) error stop 'nonfinite result'
   if (abs(area-2.0_real64) > 1e-12_real64) error stop 'integration mismatch'
   if (abs(midpoint-1.75_real64) > 1e-12_real64) error stop 'interpolation mismatch'
   if (maxval(abs(roots-[2.0_real64,3.0_real64])) > 1e-12_real64) error stop 'quadratic mismatch'
   ! The requested interval is clipped to the available tabulated domain.
   if (abs(integral(x,y,-1.0_real64,2.0_real64)-2.0_real64) > 1e-12_real64) &
      error stop 'clipped integration mismatch'
   if (ipos(1.0_real64,0.0_real64,0.75_real64,4) /= 2) error stop 'descending histogram bin'
   if (ipos(1.0_real64,0.0_real64,1.1_real64,4) /= 0) error stop 'above descending range'
   if (ipos(1.0_real64,0.0_real64,-0.1_real64,4) /= 5) error stop 'below descending range'
   if (abs(xval(0.0_real64,1.0_real64,2,3)-0.5_real64) > 1e-15_real64) &
      error stop 'bin center precision'
   print '(a,f12.8)', 'Integral of 2*x+1 on [0,1]: ', area
   print '(a,f12.8)', 'Interpolated value at 0.375: ', midpoint
   print '(a,2f10.5)', 'Roots of x**2-5*x+6: ', roots
   print *, 'Clipped integration limits and histogram bins checked'
   print *, 'PASS fortranlib'
end program
