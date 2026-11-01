! Independent MIT consumer; see licenses/special-functions-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64, int64
   use ieee_arithmetic, only: ieee_is_finite
   use stdlib_specialfunctions_gamma, only: log_gamma
   implicit none
   complex(real64),parameter :: z(24) = [ &
      cmplx(0.25_real64,-1.25_real64,kind=real64), &
      cmplx(0.25_real64,-0.25_real64,kind=real64), &
      cmplx(0.25_real64,0.25_real64,kind=real64), &
      cmplx(0.25_real64,1.25_real64,kind=real64), &
      cmplx(0.75_real64,-1.25_real64,kind=real64), &
      cmplx(0.75_real64,-0.25_real64,kind=real64), &
      cmplx(0.75_real64,0.25_real64,kind=real64), &
      cmplx(0.75_real64,1.25_real64,kind=real64), &
      cmplx(1.5_real64,-1.25_real64,kind=real64), &
      cmplx(1.5_real64,-0.25_real64,kind=real64), &
      cmplx(1.5_real64,0.25_real64,kind=real64), &
      cmplx(1.5_real64,1.25_real64,kind=real64), &
      cmplx(3.5_real64,-1.25_real64,kind=real64), &
      cmplx(3.5_real64,-0.25_real64,kind=real64), &
      cmplx(3.5_real64,0.25_real64,kind=real64), &
      cmplx(3.5_real64,1.25_real64,kind=real64), &
      cmplx(6.5_real64,-1.25_real64,kind=real64), &
      cmplx(6.5_real64,-0.25_real64,kind=real64), &
      cmplx(6.5_real64,0.25_real64,kind=real64), &
      cmplx(6.5_real64,1.25_real64,kind=real64), &
      cmplx(12.5_real64,-1.25_real64,kind=real64), &
      cmplx(12.5_real64,-0.25_real64,kind=real64), &
      cmplx(12.5_real64,0.25_real64,kind=real64), &
      cmplx(12.5_real64,1.25_real64,kind=real64) ]
   complex(real64),parameter :: expected(24) = [ &
      cmplx(-1.0946228382379026996016471_real64,1.3551598228250621885913239_real64,kind=real64), &
      cmplx(0.90447450949333888977044659_real64,0.83887024394321281804004425_real64,kind=real64), &
      cmplx(0.90447450949333888977044659_real64,-0.83887024394321281804004425_real64,kind=real64), &
      cmplx(-1.0946228382379026996016471_real64,-1.3551598228250621885913239_real64,kind=real64), &
      cmplx(-0.99449098769085145666712778_real64,0.57014986261203968249687923_real64,kind=real64), &
      cmplx(0.12685126652095696452856997_real64,0.25843254845881058131358161_real64,kind=real64), &
      cmplx(0.12685126652095696452856997_real64,-0.25843254845881058131358161_real64,kind=real64), &
      cmplx(-0.99449098769085145666712778_real64,-0.57014986261203968249687923_real64,kind=real64), &
      cmplx(-0.7473973853518807801233366_real64,-0.25417349135460030017139042_real64,kind=real64), &
      cmplx(-0.14976915644291346951437378_real64,-0.011253059956647302079273891_real64,kind=real64), &
      cmplx(-0.14976915644291346951437378_real64,0.011253059956647302079273891_real64,kind=real64), &
      cmplx(-0.7473973853518807801233366_real64,0.25417349135460030017139042_real64,kind=real64), &
      cmplx(0.94960769314614416848456846_real64,-1.4125593765521096125029208_real64,kind=real64), &
      cmplx(1.1906613360600472404428447_real64,-0.2760703898624361677368483_real64,kind=real64), &
      cmplx(1.1906613360600472404428447_real64,0.2760703898624361677368483_real64,kind=real64), &
      cmplx(0.94960769314614416848456846_real64,1.4125593765521096125029208_real64,kind=real64), &
      cmplx(5.5335659299218236731498595_real64,-2.2500067684518665720867243_real64,kind=real64), &
      cmplx(5.6573671537029799783155942_real64,-0.44829963931502034474950184_real64,kind=real64), &
      cmplx(5.6573671537029799783155942_real64,0.44829963931502034474950184_real64,kind=real64), &
      cmplx(5.5335659299218236731498595_real64,2.2500067684518665720867243_real64,kind=real64), &
      cmplx(18.669397757710808385243627_real64,-3.10874393758913529849278_real64,kind=real64), &
      cmplx(18.731745036365178422997653_real64,-0.62131696369824544082489136_real64,kind=real64), &
      cmplx(18.731745036365178422997653_real64,0.62131696369824544082489136_real64,kind=real64), &
      cmplx(18.669397757710808385243627_real64,3.10874393758913529849278_real64,kind=real64) ]
   complex(real64) :: actual
   integer :: j
   do j=1,size(z)
      actual=log_gamma(z(j))
      if(.not.ieee_is_finite(real(actual,real64)).or..not.ieee_is_finite(aimag(actual))) &
         error stop 'Nonfinite complex result'
      if(abs(actual-expected(j))>2.e-11_real64*max(1._real64,abs(expected(j)))) then
         print *, 'argument, actual, expected: ',z(j),actual,expected(j)
         error stop 'Independent complex reference'
      end if
   end do
   print '(a)', '24 complex references from independent 80/120-digit mpmath evaluations'
   print '(a)', 'PASS stdlib-complex-loggamma-reference'

end program
