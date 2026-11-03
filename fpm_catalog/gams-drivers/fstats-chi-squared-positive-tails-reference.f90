! Independent MIT consumer; see licenses/fstats-fitting-ten-drivers-MIT.txt.
program main
   use iso_fortran_env,only:wp=>real64
   use ieee_arithmetic,only:ieee_is_finite
   use fstats_chi_squared_distribution,only: &
      chi_squared_distribution
   implicit none
   type(chi_squared_distribution)::law
   real(wp),parameter::a(*)=[ &
      1.0_wp, 1.0_wp, 1.0_wp, &
      1.0_wp, 1.0_wp, 1.0_wp, &
      2.0_wp, 2.0_wp, 2.0_wp, &
      2.0_wp, 2.0_wp, 2.0_wp, &
      4.0_wp, 4.0_wp, 4.0_wp, &
      4.0_wp, 4.0_wp, 4.0_wp, &
      7.0_wp, 7.0_wp, 7.0_wp, &
      7.0_wp, 7.0_wp, 7.0_wp, &
      12.0_wp, 12.0_wp, 12.0_wp, &
      12.0_wp, 12.0_wp, 12.0_wp]
   real(wp),parameter::b(*)=[ &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp]
   real(wp),parameter::x(*)=[ &
      0.0625_wp, 0.5_wp, 1.0_wp, &
      3.0_wp, 8.0_wp, 24.0_wp, &
      0.0625_wp, 0.5_wp, 1.0_wp, &
      3.0_wp, 8.0_wp, 24.0_wp, &
      0.0625_wp, 0.5_wp, 1.0_wp, &
      3.0_wp, 8.0_wp, 24.0_wp, &
      0.0625_wp, 0.5_wp, 1.0_wp, &
      3.0_wp, 8.0_wp, 24.0_wp, &
      0.0625_wp, 0.5_wp, 1.0_wp, &
      3.0_wp, 8.0_wp, 24.0_wp]
   real(wp),parameter::pdf(*)=[ &
      1.54667246721139683_wp, 0.439391289467722397_wp, 0.24197072451914335_wp, &
      0.0513934432679230923_wp, 0.00258337316926150673_wp, 5.00346264916852372e-7_wp, &
      0.484616617238172041_wp, 0.389400391535702434_wp, 0.303265329856316712_wp, &
      0.111565080074214914_wp, 0.00915781944436709015_wp, 3.07210617666410488e-6_wp, &
      0.0151442692886928763_wp, 0.0973500978839256085_wp, 0.151632664928158356_wp, &
      0.167347620111322372_wp, 0.0366312777774683606_wp, 0.0000368652741199692586_wp, &
      0.0000251737055210188286_wp, 0.00366159407889768664_wp, 0.0161313816346095567_wp, &
      0.0925081978822615661_wp, 0.0881791375107927631_wp, 0.000461119117747371146_wp, &
      1.20355838844719539e-10_wp, 3.1689484988257034e-6_wp, 0.0000789753463167491437_wp, &
      0.00705997772344641256_wp, 0.0781467259252658359_wp, 0.00637031936793068788_wp]
   real(wp),parameter::cdf(*)=[ &
      0.197412651365847448_wp, 0.520499877813046538_wp, 0.682689492137085897_wp, &
      0.916735483336449598_wp, 0.995322265018952734_wp, 0.999999036642991357_wp, &
      0.0307667655236559182_wp, 0.221199216928595132_wp, 0.393469340287366576_wp, &
      0.776869839851570171_wp, 0.98168436111126582_wp, 0.999993855787646672_wp, &
      0.000478226946270165594_wp, 0.0264990211607439147_wp, 0.0902040104310498646_wp, &
      0.442174599628925428_wp, 0.908421805556329099_wp, 0.999920125239406733_wp, &
      4.52670017794781636e-7_wp, 0.000553518609575034511_wp, 0.00517146348348451774_wp, &
      0.114997768356849359_wp, 0.667406097400692146_wp, 0.998860648821052534_wp, &
      1.25932549840047429e-12_wp, 2.73813563382840241e-7_wp, 0.0000141649373223424907_wp, &
      0.00445598077524784919_wp, 0.214869612969594805_wp, 0.979658970583071629_wp]
   real(wp),parameter::survival(*)=[ &
      0.802587348634152552_wp, 0.479500122186953462_wp, 0.317310507862914103_wp, &
      0.0832645166635504019_wp, 0.00467773498104726584_wp, 9.63357008643094588e-7_wp, &
      0.969233234476344082_wp, 0.778800783071404868_wp, 0.606530659712633424_wp, &
      0.223130160148429829_wp, 0.0183156388887341803_wp, 6.14421235332820976e-6_wp, &
      0.999521773053729834_wp, 0.973500978839256085_wp, 0.909795989568950135_wp, &
      0.557825400371074572_wp, 0.0915781944436709015_wp, 0.0000798747605932667269_wp, &
      0.999999547329982205_wp, 0.999446481390424965_wp, 0.994828536516515482_wp, &
      0.885002231643150641_wp, 0.332593902599307854_wp, 0.00113935117894746561_wp, &
      0.999999999998740675_wp, 0.999999726186436617_wp, 0.999985835062677658_wp, &
      0.995544019224752151_wp, 0.785130387030405195_wp, 0.0203410294169283712_wp]
   integer::i

   do i=1,size(x)
      law%dof=nint(a(i))
      call probability_check(law%pdf(x(i)),pdf(i))
      call probability_check(law%cdf(x(i)),cdf(i))
      call probability_check(law%survival(x(i)),survival(i))
      if(pdf(i)>0) call check(law%log_pdf(x(i)),log(pdf(i)))
   end do
   print '(a,i0)', 'Independent distribution reference cases: ',size(x)

   print '(a)', 'PASS fstats-chi-squared-positive-tails-reference'
contains
   subroutine check(actual,expected)
      real(wp),intent(in)::actual,expected
      if(.not.ieee_is_finite(actual)) error stop 'Nonfinite result'
      if(abs(actual-expected)>2.e-10_wp*max(1._wp,abs(expected))) then
         print *, 'Actual, expected:',actual,expected
         error stop 'Independent reference'
      end if
   end subroutine
   subroutine probability_check(actual,expected)
      real(wp),intent(in)::actual,expected
      if(.not.ieee_is_finite(actual)) error stop 'Nonfinite probability'
      if(abs(actual-expected)>2.e-9_wp*max(1.e-30_wp,abs(expected))) then
         print *, 'Actual probability, expected:',actual,expected
         error stop 'Independent probability reference'
      end if
   end subroutine
   subroutine insertion_sort(x)
      real(wp),intent(inout)::x(:)
      real(wp)::value
      integer::i,j
      do i=2,size(x)
         value=x(i);j=i-1
         do while(j>=1)
            if(x(j)<=value) exit
            x(j+1)=x(j);j=j-1
         end do
         x(j+1)=value
      end do
   end subroutine
   function local_median(sorted) result(value)
      real(wp),intent(in)::sorted(:)
      real(wp)::value
      integer::n
      n=size(sorted);value=(sorted((n+1)/2)+sorted(n/2+1))/2
   end function
end program
