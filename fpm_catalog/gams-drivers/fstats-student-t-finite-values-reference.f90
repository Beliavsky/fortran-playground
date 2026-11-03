! Independent MIT consumer; see licenses/fstats-summaries-ten-drivers-MIT.txt.
program main
   use iso_fortran_env,only:wp=>real64
   use ieee_arithmetic,only:ieee_is_finite
   use fstats_t_distribution,only: &
      t_distribution
   implicit none
   type(t_distribution)::law
   real(wp),parameter::a(*)=[ &
      1.0_wp, 1.0_wp, 1.0_wp, &
      1.0_wp, 1.0_wp, 1.0_wp, &
      1.0_wp, 1.0_wp, 1.0_wp, &
      1.0_wp, 1.0_wp, 2.0_wp, &
      2.0_wp, 2.0_wp, 2.0_wp, &
      2.0_wp, 2.0_wp, 2.0_wp, &
      2.0_wp, 2.0_wp, 2.0_wp, &
      2.0_wp, 5.0_wp, 5.0_wp, &
      5.0_wp, 5.0_wp, 5.0_wp, &
      5.0_wp, 5.0_wp, 5.0_wp, &
      5.0_wp, 5.0_wp, 5.0_wp, &
      10.0_wp, 10.0_wp, 10.0_wp, &
      10.0_wp, 10.0_wp, 10.0_wp, &
      10.0_wp, 10.0_wp, 10.0_wp, &
      10.0_wp, 10.0_wp]
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
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp]
   real(wp),parameter::x(*)=[ &
      -8.0_wp, -4.0_wp, -2.0_wp, &
      -1.0_wp, -0.125_wp, 0.0_wp, &
      0.125_wp, 1.0_wp, 2.0_wp, &
      4.0_wp, 8.0_wp, -8.0_wp, &
      -4.0_wp, -2.0_wp, -1.0_wp, &
      -0.125_wp, 0.0_wp, 0.125_wp, &
      1.0_wp, 2.0_wp, 4.0_wp, &
      8.0_wp, -8.0_wp, -4.0_wp, &
      -2.0_wp, -1.0_wp, -0.125_wp, &
      0.0_wp, 0.125_wp, 1.0_wp, &
      2.0_wp, 4.0_wp, 8.0_wp, &
      -8.0_wp, -4.0_wp, -2.0_wp, &
      -1.0_wp, -0.125_wp, 0.0_wp, &
      0.125_wp, 1.0_wp, 2.0_wp, &
      4.0_wp, 8.0_wp]
   real(wp),parameter::pdf(*)=[ &
      0.00489707517205831802_wp, 0.0187241109519876866_wp, 0.0636619772367581343_wp, &
      0.159154943091895336_wp, 0.313412811011732354_wp, 0.318309886183790672_wp, &
      0.313412811011732354_wp, 0.159154943091895336_wp, 0.0636619772367581343_wp, &
      0.0187241109519876866_wp, 0.00489707517205831802_wp, 0.0018650225905959505_wp, &
      0.0130945700219731023_wp, 0.0680413817439771694_wp, 0.192450089729875255_wp, &
      0.349450282200557669_wp, 0.353553390593273762_wp, 0.349450282200557669_wp, &
      0.192450089729875255_wp, 0.0680413817439771694_wp, 0.0130945700219731023_wp, &
      0.0018650225905959505_wp, 0.000144443032695639401_wp, 0.00512372705191791425_wp, &
      0.0650903103262164663_wp, 0.219679797350980574_wp, 0.37607000437878802_wp, &
      0.379606689822494431_wp, 0.37607000437878802_wp, 0.219679797350980574_wp, &
      0.0650903103262164663_wp, 0.00512372705191791425_wp, 0.000144443032695639401_wp, &
      6.44608651405084226e-6_wp, 0.00203103391104121596_wp, 0.0611457663212181759_wp, &
      0.230361989229138647_wp, 0.385781398422957712_wp, 0.389108383966031051_wp, &
      0.385781398422957712_wp, 0.230361989229138647_wp, 0.0611457663212181759_wp, &
      0.00203103391104121596_wp, 6.44608651405084226e-6_wp]
   real(wp),parameter::cdf(*)=[ &
      0.039583424160565542_wp, 0.0779791303773693255_wp, 0.147583617650433274_wp, &
      0.25_wp, 0.460416575839434458_wp, 0.5_wp, &
      0.539583424160565542_wp, 0.75_wp, 0.852416382349566726_wp, &
      0.922020869622630675_wp, 0.960416575839434458_wp, 0.00763403608266906906_wp, &
      0.0285954792089683171_wp, 0.0917517095361369836_wp, 0.211324865405187118_wp, &
      0.455977454683718809_wp, 0.5_wp, 0.544022545316281191_wp, &
      0.788675134594812882_wp, 0.908248290463863016_wp, 0.971404520791031683_wp, &
      0.992365963917330931_wp, 0.000246453330286222042_wp, 0.0051617077404157269_wp, &
      0.0509697394149291781_wp, 0.181608733824561313_wp, 0.452696893632090147_wp, &
      0.5_wp, 0.547303106367909853_wp, 0.818391266175438687_wp, &
      0.949030260585070822_wp, 0.994838292259584273_wp, 0.999753546669713778_wp, &
      5.88747139483307989e-6_wp, 0.00125916631236834613_wp, 0.0366940173853701828_wp, &
      0.170446566151029936_wp, 0.451500357841046585_wp, 0.5_wp, &
      0.548499642158953415_wp, 0.829553433848970064_wp, 0.963305982614629817_wp, &
      0.998740833687631654_wp, 0.999994112528605167_wp]
   real(wp),parameter::survival(*)=[ &
      0.960416575839434458_wp, 0.922020869622630675_wp, 0.852416382349566726_wp, &
      0.75_wp, 0.539583424160565542_wp, 0.5_wp, &
      0.460416575839434458_wp, 0.25_wp, 0.147583617650433274_wp, &
      0.0779791303773693255_wp, 0.039583424160565542_wp, 0.992365963917330931_wp, &
      0.971404520791031683_wp, 0.908248290463863016_wp, 0.788675134594812882_wp, &
      0.544022545316281191_wp, 0.5_wp, 0.455977454683718809_wp, &
      0.211324865405187118_wp, 0.0917517095361369836_wp, 0.0285954792089683171_wp, &
      0.00763403608266906906_wp, 0.999753546669713778_wp, 0.994838292259584273_wp, &
      0.949030260585070822_wp, 0.818391266175438687_wp, 0.547303106367909853_wp, &
      0.5_wp, 0.452696893632090147_wp, 0.181608733824561313_wp, &
      0.0509697394149291781_wp, 0.0051617077404157269_wp, 0.000246453330286222042_wp, &
      0.999994112528605167_wp, 0.998740833687631654_wp, 0.963305982614629817_wp, &
      0.829553433848970064_wp, 0.548499642158953415_wp, 0.5_wp, &
      0.451500357841046585_wp, 0.170446566151029936_wp, 0.0366940173853701828_wp, &
      0.00125916631236834613_wp, 5.88747139483307989e-6_wp]
   integer::i

   do i=1,size(x)
      law%dof=a(i)
      call probability_check(law%pdf(x(i)),pdf(i))
      call probability_check(law%cdf(x(i)),cdf(i))
      call probability_check(law%survival(x(i)),survival(i))
      if(pdf(i)>0) call check(law%log_pdf(x(i)),log(pdf(i)))
   end do
   print '(a,i0)', 'Independent distribution reference cases: ',size(x)

   print '(a)', 'PASS fstats-student-t-finite-values-reference'
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
