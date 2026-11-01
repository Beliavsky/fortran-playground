! Independent MIT consumer; see licenses/distribution-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64
   use ieee_arithmetic, only: ieee_is_finite
   use stdlib_stats_distribution_normal, only: cdf_normal
   implicit none
   real(real64),parameter :: reference(65)=[ &
      6.2209605742717841235159952e-16_real64, &
      4.5946274357785954601554549e-15_real64, &
      3.1908916729108962277672883e-14_real64, &
      2.0838581586720694311899976e-13_real64, &
      1.2798125438858350043836237e-12_real64, &
      7.3922577780178224195162297e-12_real64, &
      4.0160005838591178083461454e-11_real64, &
      2.0522634252189388816227636e-10_real64, &
      9.8658764503769814070086413e-10_real64, &
      4.4621724539016118730692226e-9_real64, &
      1.8989562465887719383851274e-8_real64, &
      7.6049605164887142511460651e-8_real64, &
      0.00000028665157187919391167375233_real64, &
      0.0000010170832425687031712591823_real64, &
      0.0000033976731247300604016874492_real64, &
      0.000010688525774934420469200558_real64, &
      0.000031671241833119921253770757_real64, &
      0.000088417285200803867817754669_real64, &
      0.00023262907903552503634992589_real64, &
      0.00057702504239076704291691931_real64, &
      0.0013498980316300945266518148_real64, &
      0.002979763235054556754294247_real64, &
      0.0062096653257761351669781046_real64, &
      0.012224472655044703152623931_real64, &
      0.022750131948179207200282637_real64, &
      0.04005915686381709041875735_real64, &
      0.066807201268858066004494041_real64, &
      0.10564977366685525768877276_real64, &
      0.15865525393145705141476745_real64, &
      0.22662735237686819932706217_real64, &
      0.30853753872598689636229539_real64, &
      0.40129367431707627575914621_real64, &
      0.5_real64, &
      0.59870632568292372424085379_real64, &
      0.69146246127401310363770461_real64, &
      0.77337264762313180067293783_real64, &
      0.84134474606854294858523255_real64, &
      0.89435022633314474231122724_real64, &
      0.93319279873114193399550596_real64, &
      0.95994084313618290958124265_real64, &
      0.97724986805182079279971736_real64, &
      0.98777552734495529684737607_real64, &
      0.9937903346742238648330219_real64, &
      0.99702023676494544324570575_real64, &
      0.99865010196836990547334819_real64, &
      0.99942297495760923295708308_real64, &
      0.99976737092096447496365007_real64, &
      0.99991158271479919613218225_real64, &
      0.99996832875816688007874623_real64, &
      0.9999893114742250655795308_real64, &
      0.99999660232687526993959831_real64, &
      0.99999898291675743129682874_real64, &
      0.99999971334842812080608833_real64, &
      0.99999992395039483511285749_real64, &
      0.99999998101043753411228062_real64, &
      0.99999999553782754609838813_real64, &
      0.99999999901341235496230186_real64, &
      0.99999999979477365747810611_real64, &
      0.99999999995983999416140882_real64, &
      0.99999999999260774222198218_real64, &
      0.99999999999872018745611416_real64, &
      0.99999999999979161418413279_real64, &
      0.99999999999996809108327089_real64, &
      0.99999999999999540537256422_real64, &
      0.99999999999999937790394257_real64 ]
   real(real64),parameter :: locations(3)=[-1.5_real64,0._real64,2.25_real64]
   real(real64),parameter :: scales(3)=[0.25_real64,1._real64,4._real64]
   real(real64) :: x,z,expected,actual,previous
   integer :: a,b,i,checks
   checks=0
   do a=1,3
      do b=1,3
         previous=0
         do i=1,65
            z=real(i-33,real64)/4
            x=locations(a)+scales(b)*z
            expected=reference(i)
            actual=cdf_normal(x,locations(a),scales(b))
            call verify(actual,expected)
            checks=checks+1
         end do
      end do
   end do
   print '(a,i0)', 'Normal references from independent 80/120-digit constants, z=-8..8, nine location/scale pairs: ',checks
   print '(a)', 'PASS stdlib-normal-cdf-reference'
contains
   subroutine verify(actual,expected)
      real(real64),intent(in) :: actual,expected
      if(.not.ieee_is_finite(actual)) error stop 'Nonfinite distribution result'
      if(actual<0._real64) error stop 'Negative distribution result'
      if(abs(actual-expected)>3.e-14_real64*max(1._real64,abs(expected))) then
         print *, 'actual, expected: ',actual,expected
         error stop 'Independent distribution reference'
      end if
      if(actual>1._real64) error stop 'CDF exceeds one'
      if(actual+3.e-14_real64<previous) error stop 'Nonmonotone CDF'
      previous=actual
   end subroutine
end program
