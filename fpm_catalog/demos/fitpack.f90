program main
   use fitpack, only: fitpack_curve, FP_REAL, FP_FLAG, FITPACK_SUCCESS
   implicit none
   type(fitpack_curve) :: curve
   real(FP_REAL) :: x(6), y(6), value, slope
   integer(FP_FLAG) :: status
   integer :: i
   x = [(real(i-1,FP_REAL)/5,i=1,6)]
   y = x*x
   status = curve%new_fit(x,y,smoothing=0.0_FP_REAL)
   if (.not. FITPACK_SUCCESS(status)) error stop 'spline fit failed'
   value = curve%eval(0.5_FP_REAL,status)
   if (.not. FITPACK_SUCCESS(status)) error stop 'evaluation failed'
   if (abs(value-0.25_FP_REAL) > 1.e-10_FP_REAL) error stop 'incorrect value'
   slope = curve%dfdx(0.5_FP_REAL,order=1,ierr=status)
   if (.not. FITPACK_SUCCESS(status)) error stop 'derivative failed'
   if (abs(slope-1.0_FP_REAL) > 1.e-10_FP_REAL) error stop 'incorrect derivative'
   print *, 'Spline value and derivative at x=0.5:', value, slope
   call curve%destroy()
   print *, 'PASS fitpack'
end program main
