! Independent MIT consumer; see licenses/distribution-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64
   use ieee_arithmetic, only: ieee_is_finite
   use stdlib_stats_distribution_gamma, only: pdf_gamma
   implicit none
   real(real64),parameter :: reference(9,6)=reshape([ &
      0.0_real64, &
      1.0_real64, &
      0.88249690258459540286489214_real64, &
      0.77880078307140486824517027_real64, &
      0.60653065971263342360379953_real64, &
      0.36787944117144232159552377_real64, &
      0.13533528323661269189399949_real64, &
      0.018315638888734180293718021_real64, &
      0.00033546262790251183882138913_real64, &
      0.0_real64, &
      0.0_real64, &
      0.35206532676429947777468044_real64, &
      0.43939128946772239704686198_real64, &
      0.48394144903828669959566039_real64, &
      0.41510749742059470334026825_real64, &
      0.2159638660527522078022568_real64, &
      0.041333970708184107714137883_real64, &
      0.0010706418061190828141925959_real64, &
      0.0_real64, &
      0.0_real64, &
      0.029338777230358289814556703_real64, &
      0.073231881577953732841143663_real64, &
      0.1613138163460955665318868_real64, &
      0.2767383316137298022268455_real64, &
      0.28795182140366961040300907_real64, &
      0.11022392188849095390436769_real64, &
      0.0057100896326351083423605115_real64, &
      0.0_real64, &
      0.0_real64, &
      0.0068945070514421515848819699_real64, &
      0.024337524470981402132661571_real64, &
      0.075816332464079177950474942_real64, &
      0.18393972058572116079776189_real64, &
      0.27067056647322538378799899_real64, &
      0.14652511110987344234974417_real64, &
      0.010734804092880378842284452_real64, &
      0.0_real64, &
      0.0_real64, &
      0.0000089772227232319682094817316_real64, &
      0.00012675793995302813610761235_real64, &
      0.001579506926334982873968228_real64, &
      0.015328310048810096733146824_real64, &
      0.090223522157741794595999663_real64, &
      0.19536681481316458979965889_real64, &
      0.057252288495362020492183744_real64, &
      0.0_real64, &
      0.0_real64, &
      8.3493514911011609091161938e-11_real64, &
      9.4313943417431648889592521e-9_real64, &
      0.00000094018269424701361545727855_real64, &
      0.000072991952613381413014984875_real64, &
      0.00343708655839016360365713_real64, &
      0.059540362609726351177038901_real64, &
      0.1395865319505969261523718_real64 ],[9,6])
   real(real64),parameter :: shapes(6)=[ &
      1.0_real64, &
      1.5_real64, &
      2.5_real64, &
      3.0_real64, &
      5.0_real64, &
      8.0_real64 ]
   real(real64),parameter :: zvalues(9)=[ &
      -0.25_real64, &
      0.0_real64, &
      0.125_real64, &
      0.25_real64, &
      0.5_real64, &
      1.0_real64, &
      2.0_real64, &
      4.0_real64, &
      8.0_real64 ]
   real(real64),parameter :: locations(3)=[-1.5_real64,0._real64,2.25_real64]
   real(real64),parameter :: rates(3)=[0.25_real64,1._real64,4._real64]
   real(real64) :: x,z,expected,actual,previous
   integer :: a,b,i,j,checks
   checks=0
   do a=1,3
      do b=1,3
         do j=1,size(shapes)
            previous=0
            do i=1,9
               z=zvalues(i)
               x=locations(a)+z/rates(b)
               expected=reference(i,j)*rates(b)
               actual=pdf_gamma(x,shapes(j),rates(b),loc=locations(a))
               call verify(actual,expected)
               checks=checks+1
            end do
         end do
      end do
   end do
   print '(a,i0)', 'Gamma references at integer/noninteger shapes, three locations/rates and nine support/tail points: ',checks
   print '(a)', 'PASS stdlib-gamma-pdf-reference'
contains
   subroutine verify(actual,expected)
      real(real64),intent(in) :: actual,expected
      if(.not.ieee_is_finite(actual)) error stop 'Nonfinite distribution result'
      if(actual<0._real64) error stop 'Negative distribution result'
      if(abs(actual-expected)>3.e-12_real64*max(1._real64,abs(expected))) then
         print *, 'actual, expected: ',actual,expected
         error stop 'Independent distribution reference'
      end if
   end subroutine
end program
