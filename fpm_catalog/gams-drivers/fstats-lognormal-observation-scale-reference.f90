! Independent MIT consumer; see licenses/fstats-fitting-ten-drivers-MIT.txt.
program main
   use iso_fortran_env,only:wp=>real64
   use ieee_arithmetic,only:ieee_is_finite
   use fstats_log_normal_distribution,only: &
      log_normal_distribution
   implicit none
   type(log_normal_distribution)::law
   real(wp),parameter::a(*)=[ &
      -1.0_wp, -1.0_wp, -1.0_wp, &
      -1.0_wp, -1.0_wp, -1.0_wp, &
      -1.0_wp, -1.0_wp, -1.0_wp, &
      -1.0_wp, -1.0_wp, -1.0_wp, &
      -1.0_wp, -1.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 1.0_wp, 1.0_wp, &
      1.0_wp, 1.0_wp, 1.0_wp, &
      1.0_wp, 1.0_wp, 1.0_wp, &
      1.0_wp, 1.0_wp, 1.0_wp, &
      1.0_wp, 1.0_wp, 1.0_wp]
   real(wp),parameter::b(*)=[ &
      0.5_wp, 0.5_wp, 0.5_wp, &
      0.5_wp, 0.5_wp, 0.5_wp, &
      0.5_wp, 2.0_wp, 2.0_wp, &
      2.0_wp, 2.0_wp, 2.0_wp, &
      2.0_wp, 2.0_wp, 0.5_wp, &
      0.5_wp, 0.5_wp, 0.5_wp, &
      0.5_wp, 0.5_wp, 0.5_wp, &
      2.0_wp, 2.0_wp, 2.0_wp, &
      2.0_wp, 2.0_wp, 2.0_wp, &
      2.0_wp, 0.5_wp, 0.5_wp, &
      0.5_wp, 0.5_wp, 0.5_wp, &
      0.5_wp, 0.5_wp, 2.0_wp, &
      2.0_wp, 2.0_wp, 2.0_wp, &
      2.0_wp, 2.0_wp, 2.0_wp]
   real(wp),parameter::x(*)=[ &
      -1.0_wp, 0.0_wp, 0.0625_wp, &
      0.5_wp, 1.0_wp, 2.0_wp, &
      16.0_wp, -1.0_wp, 0.0_wp, &
      0.0625_wp, 0.5_wp, 1.0_wp, &
      2.0_wp, 16.0_wp, -1.0_wp, &
      0.0_wp, 0.0625_wp, 0.5_wp, &
      1.0_wp, 2.0_wp, 16.0_wp, &
      -1.0_wp, 0.0_wp, 0.0625_wp, &
      0.5_wp, 1.0_wp, 2.0_wp, &
      16.0_wp, -1.0_wp, 0.0_wp, &
      0.0625_wp, 0.5_wp, 1.0_wp, &
      2.0_wp, 16.0_wp, -1.0_wp, &
      0.0_wp, 0.0625_wp, 0.5_wp, &
      1.0_wp, 2.0_wp, 16.0_wp]
   real(wp),parameter::pdf(*)=[ &
      0.0_wp, 0.0_wp, 0.0238172734384205261_wp, &
      1.32185826393393575_wp, 0.107981933026376104_wp, 0.00129087721087298413_wp, &
      2.16616840029205615e-14_wp, 0.0_wp, 0.0_wp, &
      2.15489966045669417_wp, 0.394274321376052422_wp, 0.176032663382149739_wp, &
      0.0696985115731827043_wp, 0.0021043941996647404_wp, 0.0_wp, &
      0.0_wp, 2.68535109802337901e-6_wp, 0.610455304190183071_wp, &
      0.797884560802865356_wp, 0.152613826047545768_wp, 1.04896527266538242e-8_wp, &
      0.0_wp, 0.0_wp, 1.22091060838036614_wp, &
      0.375688416016771192_wp, 0.199471140200716339_wp, 0.093922104004192798_wp, &
      0.00476918206398580524_wp, 0.0_wp, 0.0_wp, &
      5.54539110474766374e-12_wp, 0.00516350884349193653_wp, 0.107981933026376104_wp, &
      0.330464565983483938_wp, 0.00009303622436883018_wp, 0.0_wp, &
      0.0_wp, 0.538724915114173543_wp, 0.278794046292730817_wp, &
      0.176032663382149739_wp, 0.0985685803440131055_wp, 0.00841757679865896161_wp]
   real(wp),parameter::cdf(*)=[ &
      0.0_wp, 0.0_wp, 0.000196174431404364705_wp, &
      0.730295069265090492_wp, 0.977249868051820793_wp, 0.999645783255333811_wp, &
      0.999999999999977416_wp, 0.0_wp, 0.0_wp, &
      0.18772946342505247_wp, 0.560968990252310574_wp, 0.691462461274013104_wp, &
      0.801383580242638722_wp, 0.970372350633342655_wp, 0.0_wp, &
      0.0_wp, 1.46828105639037271e-8_wp, 0.0828285190016984853_wp, &
      0.5_wp, 0.917171480998301515_wp, 0.999999985317189436_wp, &
      0.0_wp, 0.0_wp, 0.0828285190016984853_wp, &
      0.364455844736535717_wp, 0.5_wp, 0.635544155263464283_wp, &
      0.917171480998301515_wp, 0.0_wp, 0.0_wp, &
      2.25836044469473647e-14_wp, 0.000354216744666189438_wp, 0.0227501319481792072_wp, &
      0.269704930734909508_wp, 0.999803825568595635_wp, 0.0_wp, &
      0.0_wp, 0.0296276493666573449_wp, 0.198616419757361278_wp, &
      0.308537538725986896_wp, 0.439031009747689426_wp, 0.81227053657494753_wp]
   real(wp),parameter::survival(*)=[ &
      1.0_wp, 1.0_wp, 0.999803825568595635_wp, &
      0.269704930734909508_wp, 0.0227501319481792072_wp, 0.000354216744666189438_wp, &
      2.25836044469473647e-14_wp, 1.0_wp, 1.0_wp, &
      0.81227053657494753_wp, 0.439031009747689426_wp, 0.308537538725986896_wp, &
      0.198616419757361278_wp, 0.0296276493666573449_wp, 1.0_wp, &
      1.0_wp, 0.999999985317189436_wp, 0.917171480998301515_wp, &
      0.5_wp, 0.0828285190016984853_wp, 1.46828105639037271e-8_wp, &
      1.0_wp, 1.0_wp, 0.917171480998301515_wp, &
      0.635544155263464283_wp, 0.5_wp, 0.364455844736535717_wp, &
      0.0828285190016984853_wp, 1.0_wp, 1.0_wp, &
      0.999999999999977416_wp, 0.999645783255333811_wp, 0.977249868051820793_wp, &
      0.730295069265090492_wp, 0.000196174431404364705_wp, 1.0_wp, &
      1.0_wp, 0.970372350633342655_wp, 0.801383580242638722_wp, &
      0.691462461274013104_wp, 0.560968990252310574_wp, 0.18772946342505247_wp]
   integer::i

   do i=1,size(x)
      law%mean_value=a(i);law%standard_deviation=b(i)
      call probability_check(law%pdf(x(i)),pdf(i))
      call probability_check(law%cdf(x(i)),cdf(i))
      call probability_check(law%survival(x(i)),survival(i))
      if(pdf(i)>0) call check(law%log_pdf(x(i)),log(pdf(i)))
   end do
   print '(a,i0)', 'Independent distribution reference cases: ',size(x)

   print '(a)', 'PASS fstats-lognormal-observation-scale-reference'
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
