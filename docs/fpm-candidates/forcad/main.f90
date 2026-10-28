program demo_forcad
   use forcad, only: rk, nurbs_curve
   use pyplot_module, only: pyplot
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   type(nurbs_curve) :: curve
   type(pyplot) :: plot
   real(rk) :: control(3,3), t, expected(3), length
   real(rk), allocatable :: points(:,:)
   integer :: i, status

   control(1,:) = [0._rk, 0._rk, 0._rk]
   control(2,:) = [1._rk, 2._rk, 0._rk]
   control(3,:) = [2._rk, 0._rk, 0._rk]
   call curve%set(control, [1._rk, 1._rk, 1._rk])
   call curve%create(res=41)
   points = curve%get_Xg()
   if (any(shape(points) /= [41,3])) error stop 'Unexpected curve dimensions'
   if (.not. all(ieee_is_finite(points))) error stop 'Nonfinite curve'
   do i = 1, 41
      t = real(i-1,rk)/40._rk
      expected = (1._rk-t)**2*control(1,:) + 2._rk*t*(1._rk-t)*control(2,:) + t**2*control(3,:)
      if (maxval(abs(points(i,:)-expected)) > 1.e-10_rk) error stop 'Bezier curve check failed'
   end do
   call curve%cmp_length(length, ngauss=24)
   if (.not. ieee_is_finite(length)) error stop 'Nonfinite curve length'
   if (abs(length - (sqrt(5._rk)+0.5_rk*asinh(2._rk))) > 1.e-8_rk) &
      error stop 'Curve length check failed'
   print '(a,2f10.5)', 'Curve midpoint:', points(21,1:2)
   print '(a,f14.10)', 'Curve length: ', length
   call plot%initialize(grid=.true., legend=.true., xlabel='x', ylabel='y', &
      title='Quadratic Bezier curve', use_oo_api=.true.)
   call plot%add_plot(points(:,1), points(:,2), label='Curve', linestyle='b-')
   call plot%add_plot(control(:,1), control(:,2), label='Control polygon', linestyle='ro--')
   call plot%savefig('bezier.png', pyfile='bezier.py', istat=status)
   if (status /= 0) error stop 'Plot generation failed'
   call curve%finalize()
   print *, 'PASS forcad'
end program demo_forcad
