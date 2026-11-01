! Independent MIT consumer; see licenses/distribution-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64
   use ieee_arithmetic, only: ieee_is_finite
   use stdlib_stats_distribution_gamma, only: cdf_gamma
   implicit none
   real(real64),parameter :: reference(9,7)=reshape([ &
      0.0_real64, &
      0.0_real64, &
      0.38292492254802620727540922_real64, &
      0.52049987781304653768274665_real64, &
      0.68268949213708589717046509_real64, &
      0.84270079294971486934122064_real64, &
      0.95449973610364158559943473_real64, &
      0.99532226501895273416206926_real64, &
      0.99993665751633376015749246_real64, &
      0.0_real64, &
      0.0_real64, &
      0.11750309741540459713510786_real64, &
      0.22119921692859513175482973_real64, &
      0.39346934028736657639620047_real64, &
      0.63212055882855767840447623_real64, &
      0.86466471676338730810600051_real64, &
      0.98168436111126581970628198_real64, &
      0.99966453737209748816117861_real64, &
      0.0_real64, &
      0.0_real64, &
      0.03085959578372672950072878_real64, &
      0.081108588345324140635884676_real64, &
      0.19874804309879919757480471_real64, &
      0.42759329552912016600095239_real64, &
      0.73853587005088937779717792_real64, &
      0.95398829431076862644793137_real64, &
      0.99886601571021467734329986_real64, &
      0.0_real64, &
      0.0_real64, &
      0.0015208185533684396861720762_real64, &
      0.0078767067673704077947410136_real64, &
      0.03743422675270363104291791_real64, &
      0.15085496391539036377410689_real64, &
      0.45058404864721976739416886_real64, &
      0.84376437242227767254356369_real64, &
      0.99315592607757956900093935_real64, &
      0.0_real64, &
      0.0_real64, &
      0.000296477540888020192114369_real64, &
      0.0021614966897625125608755954_real64, &
      0.014387677966970686643825756_real64, &
      0.080301397071394196011190575_real64, &
      0.32332358381693654053000253_real64, &
      0.76189669444645565618166572_real64, &
      0.98624603225599701460832305_real64, &
      0.0_real64, &
      0.0_real64, &
      0.00000022919102136524120147185553_real64, &
      0.0000066117105610342470461855156_real64, &
      0.00017211562995584077811170404_real64, &
      0.0036598468273437123454564558_real64, &
      0.052653017343711156742003535_real64, &
      0.37116306482012647658234794_real64, &
      0.90036759951295398387004743_real64, &
      0.0_real64, &
      0.0_real64, &
      1.3229345143345166160128734e-12_real64, &
      3.0312747228845902507991185e-10_real64, &
      6.2196908637286483022064229e-8_real64, &
      0.000010249196674641694707212061_real64, &
      0.0010967189678587026871465847_real64, &
      0.051133615792847339005763844_real64, &
      0.54703919051300551454685632_real64 ],[9,7])
   real(real64),parameter :: shapes(7)=[ &
      0.5_real64, &
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
               expected=reference(i,j)
               actual=cdf_gamma(x,shapes(j),rates(b),loc=locations(a))
               call verify(actual,expected)
               checks=checks+1
            end do
         end do
      end do
   end do
   print '(a,i0)', 'Gamma references at integer/noninteger shapes, three locations/rates and nine support/tail points: ',checks
   print '(a)', 'PASS stdlib-gamma-cdf-reference'
contains
   subroutine verify(actual,expected)
      real(real64),intent(in) :: actual,expected
      if(.not.ieee_is_finite(actual)) error stop 'Nonfinite distribution result'
      if(actual<0._real64) error stop 'Negative distribution result'
      if(abs(actual-expected)>3.e-12_real64*max(1._real64,abs(expected))) then
         print *, 'actual, expected: ',actual,expected
         error stop 'Independent distribution reference'
      end if
      if(actual>1._real64) error stop 'CDF exceeds one'
      if(actual+3.e-14_real64<previous) error stop 'Nonmonotone CDF'
      previous=actual
   end subroutine
end program
