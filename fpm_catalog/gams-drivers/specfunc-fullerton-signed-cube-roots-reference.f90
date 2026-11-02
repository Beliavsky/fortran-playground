! Independent MIT consumer; see licenses/gamma-relative-ten-drivers-MIT.txt.
program main
   use iso_fortran_env,only:wp=>real64
   use ieee_arithmetic,only:ieee_is_finite
   use specfunc_fullerton,only:cbrt
   implicit none
   real(wp),parameter::aa(*)=[ &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp]
   real(wp),parameter::xx(*)=[ &
      -2.1663950687494155e+27_wp, -1.5474250491067253e+27_wp, -1.2379400392853803e+27_wp, &
      -1879048192.0_wp, -1342177280.0_wp, -1073741824.0_wp, &
      -896.0_wp, -640.0_wp, -512.0_wp, &
      -14.0_wp, -10.0_wp, -8.0_wp, &
      -1.75_wp, -1.25_wp, -1.0_wp, &
      -0.21875_wp, -0.15625_wp, -0.125_wp, &
      -0.00341796875_wp, -0.00244140625_wp, -0.001953125_wp, &
      -1.6298145055770874e-09_wp, -1.1641532182693481e-09_wp, -9.313225746154785e-10_wp, &
      -1.4136387421560532e-27_wp, -1.0097419586828951e-27_wp, -8.077935669463161e-28_wp, &
      0.0_wp, 8.077935669463161e-28_wp, 1.0097419586828951e-27_wp, &
      1.4136387421560532e-27_wp, 9.313225746154785e-10_wp, 1.1641532182693481e-09_wp, &
      1.6298145055770874e-09_wp, 0.001953125_wp, 0.00244140625_wp, &
      0.00341796875_wp, 0.125_wp, 0.15625_wp, &
      0.21875_wp, 1.0_wp, 1.25_wp, &
      1.75_wp, 8.0_wp, 10.0_wp, &
      14.0_wp, 512.0_wp, 640.0_wp, &
      896.0_wp, 1073741824.0_wp, 1342177280.0_wp, &
      1879048192.0_wp, 1.2379400392853803e+27_wp, 1.5474250491067253e+27_wp, &
      2.1663950687494155e+27_wp]
   real(wp),parameter::expected(*)=[ &
      -1293935275.41750065_wp, -1156653316.88185472_wp, -1073741824.0_wp, &
      -1233.99283925771775_wp, -1103.07056129632447_wp, -1024.0_wp, &
      -9.64056905670091994_wp, -8.61773876012753489_wp, -8.0_wp, &
      -2.41014226417522999_wp, -2.15443469003188372_wp, -2.0_wp, &
      -1.20507113208761499_wp, -1.07721734501594186_wp, -1.0_wp, &
      -0.602535566043807497_wp, -0.53860867250797093_wp, -0.5_wp, &
      -0.150633891510951874_wp, -0.134652168126992733_wp, -0.125_wp, &
      -0.00117682727742931152_wp, -0.00105197006349213072_wp, -0.0009765625_wp, &
      -1.12230994933062698e-9_wp, -1.00323683118069718e-9_wp, -9.31322574615478516e-10_wp, &
      0.0_wp, 9.31322574615478516e-10_wp, 1.00323683118069718e-9_wp, &
      1.12230994933062698e-9_wp, 0.0009765625_wp, 0.00105197006349213072_wp, &
      0.00117682727742931152_wp, 0.125_wp, 0.134652168126992733_wp, &
      0.150633891510951874_wp, 0.5_wp, 0.53860867250797093_wp, &
      0.602535566043807497_wp, 1.0_wp, 1.07721734501594186_wp, &
      1.20507113208761499_wp, 2.0_wp, 2.15443469003188372_wp, &
      2.41014226417522999_wp, 8.0_wp, 8.61773876012753489_wp, &
      9.64056905670091994_wp, 1024.0_wp, 1103.07056129632447_wp, &
      1233.99283925771775_wp, 1073741824.0_wp, 1156653316.88185472_wp, &
      1293935275.41750065_wp]
   integer,parameter::orders(*)=[ &
      0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0, &
      0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0, &
      0,0,0,0,0]
   real(wp)::actual,error,maximum_error
   real::logvalue,sgn
   integer::i
   maximum_error=0
   do i=1,size(expected)
      actual=real(cbrt(real(xx(i))),wp)
      if(.not.ieee_is_finite(actual)) error stop 'Nonfinite result'
      error=abs(actual-expected(i))/max(abs(expected(i)),1.e-30_wp)
      if(error>5.e-5_wp) then
         print *, 'Case, a, x, n, actual, reference:',i,aa(i),xx(i),orders(i),actual,expected(i)
         error stop 'Independent high precision reference'
      end if
      maximum_error=max(maximum_error,error)
   end do
   print '(a,i0)', 'Default REAL32 comparisons with independent high precision references: ',size(expected)
   print '(a,es12.4)', 'Maximum relative error (reference floor 1e-30): ',maximum_error
   print '(a)', 'PASS specfunc-fullerton-signed-cube-roots-reference'
end program
