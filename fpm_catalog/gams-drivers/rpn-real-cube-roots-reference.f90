! Independent MIT consumer; see licenses/next-numerical-drivers-MIT.txt.
program main
   use iso_fortran_env,only:real64
   use assert,only:wp
   use funcs,only:cuberoot
   use ieee_arithmetic,only:ieee_is_finite
   implicit none
   real(wp),parameter::x(*)=[ &
      0.0_wp, -8.077935669463161e-28_wp, 8.077935669463161e-28_wp, &
      -1.5777218104420236e-27_wp, 1.5777218104420236e-27_wp, -4.329268647852913e-27_wp, &
      4.329268647852913e-27_wp, -2.842170943040401e-14_wp, 2.842170943040401e-14_wp, &
      -5.551115123125783e-14_wp, 5.551115123125783e-14_wp, -1.5232259897857148e-13_wp, &
      1.5232259897857148e-13_wp, -0.001953125_wp, 0.001953125_wp, &
      -0.003814697265625_wp, 0.003814697265625_wp, -0.010467529296875_wp, &
      0.010467529296875_wp, -1.0_wp, 1.0_wp, &
      -1.953125_wp, 1.953125_wp, -5.359375_wp, &
      5.359375_wp, -512.0_wp, 512.0_wp, &
      -1000.0_wp, 1000.0_wp, -2744.0_wp, &
      2744.0_wp, -35184372088832.0_wp, 35184372088832.0_wp, &
      -68719476736000.0_wp, 68719476736000.0_wp, -188566244163584.0_wp, &
      188566244163584.0_wp, -1.2379400392853803e+27_wp, 1.2379400392853803e+27_wp, &
      -2.4178516392292583e+27_wp, 2.4178516392292583e+27_wp, -6.634584898045085e+27_wp, &
      6.634584898045085e+27_wp, -0.125_wp, 0.125_wp, &
      -0.5_wp, 0.5_wp, -2.0_wp, &
      2.0_wp, -3.0_wp, 3.0_wp, &
      -5.0_wp, 5.0_wp, -4.25_wp, &
      4.25_wp]
   real(wp),parameter::expected(*)=[ &
      0.0_wp, -9.31322574615478516e-10_wp, 9.31322574615478516e-10_wp, &
      -1.16415321826934814e-9_wp, 1.16415321826934814e-9_wp, -1.6298145055770874e-9_wp, &
      1.6298145055770874e-9_wp, -0.000030517578125_wp, 0.000030517578125_wp, &
      -0.00003814697265625_wp, 0.00003814697265625_wp, -0.00005340576171875_wp, &
      0.00005340576171875_wp, -0.125_wp, 0.125_wp, &
      -0.15625_wp, 0.15625_wp, -0.21875_wp, &
      0.21875_wp, -1.0_wp, 1.0_wp, &
      -1.25_wp, 1.25_wp, -1.75_wp, &
      1.75_wp, -8.0_wp, 8.0_wp, &
      -10.0_wp, 10.0_wp, -14.0_wp, &
      14.0_wp, -32768.0_wp, 32768.0_wp, &
      -40960.0_wp, 40960.0_wp, -57344.0_wp, &
      57344.0_wp, -1073741824.0_wp, 1073741824.0_wp, &
      -1342177280.0_wp, 1342177280.0_wp, -1879048192.0_wp, &
      1879048192.0_wp, -0.5_wp, 0.5_wp, &
      -0.793700525984099737_wp, 0.793700525984099737_wp, -1.25992104989487316_wp, &
      1.25992104989487316_wp, -1.44224957030740838_wp, 1.44224957030740838_wp, &
      -1.70997594667669699_wp, 1.70997594667669699_wp, -1.61980590063874169_wp, &
      1.61980590063874169_wp]
   real(wp)::value
   integer::i
   if(wp/=real64) error stop 'Expected real64 cuberoot'
   do i=1,size(x)
      value=cuberoot(x(i))
      call check(value,expected(i))
      if(x(i)/=0.and.sign(1._wp,value)/=sign(1._wp,x(i))) error stop 'Root sign'
      if(x(i)/=0) call check(value**3,x(i))
   end do
   print '(a,i0)', 'Independent high precision reference points: ',size(x)
   print '(a)', 'PASS rpn-real-cube-roots-reference'
contains
   subroutine check(actual,expected)
      real(wp),intent(in)::actual,expected
      if(.not.ieee_is_finite(actual)) error stop 'Nonfinite result'
      if(abs(actual-expected)>2.e-12_wp*max(abs(expected),1.e-100_wp)) then
         print *, 'Actual, expected:',actual,expected
         error stop 'Independent reference'
      end if
   end subroutine
end program
