! Independent MIT consumer; see licenses/fstats-fitting-ten-drivers-MIT.txt.
program main
   use iso_fortran_env,only:wp=>real64
   use ieee_arithmetic,only:ieee_is_finite
   use fstats_f_distribution,only: &
      f_distribution
   implicit none
   type(f_distribution)::law
   real(wp),parameter::a(*)=[ &
      1.0_wp, 1.0_wp, 1.0_wp, &
      1.0_wp, 1.0_wp, 2.0_wp, &
      2.0_wp, 2.0_wp, 2.0_wp, &
      2.0_wp, 5.0_wp, 5.0_wp, &
      5.0_wp, 5.0_wp, 5.0_wp, &
      10.0_wp, 10.0_wp, 10.0_wp, &
      10.0_wp, 10.0_wp]
   real(wp),parameter::b(*)=[ &
      1.0_wp, 1.0_wp, 1.0_wp, &
      1.0_wp, 1.0_wp, 4.0_wp, &
      4.0_wp, 4.0_wp, 4.0_wp, &
      4.0_wp, 9.0_wp, 9.0_wp, &
      9.0_wp, 9.0_wp, 9.0_wp, &
      3.0_wp, 3.0_wp, 3.0_wp, &
      3.0_wp, 3.0_wp]
   real(wp),parameter::x(*)=[ &
      0.03125_wp, 0.25_wp, 1.0_wp, &
      3.0_wp, 16.0_wp, 0.03125_wp, &
      0.25_wp, 1.0_wp, 3.0_wp, &
      16.0_wp, 0.03125_wp, 0.25_wp, &
      1.0_wp, 3.0_wp, 16.0_wp, &
      0.03125_wp, 0.25_wp, 1.0_wp, &
      3.0_wp, 16.0_wp]
   real(wp),parameter::pdf(*)=[ &
      1.74606800709256935_wp, 0.509295817894065074_wp, 0.159154943091895336_wp, &
      0.0459440746184826708_wp, 0.00468102773799692164_wp, 0.954552571688666363_wp, &
      0.70233196159122085_wp, 0.296296296296296296_wp, 0.064_wp, &
      0.00137174211248285322_wp, 0.0524589852558588424_wp, 0.538779797247407994_wp, &
      0.486040095471822741_wp, 0.0580458984014386675_wp, 0.0000741341435619871679_wp, &
      0.00278953604354759704_wp, 0.423201997307928051_wp, 0.404122811488562683_wp, &
      0.0767873297430462157_wp, 0.00192488885385202328_wp]
   real(wp),parameter::cdf(*)=[ &
      0.111388754023063788_wp, 0.295167235300866548_wp, 0.5_wp, &
      0.666666666666666667_wp, 0.844041739245261349_wp, 0.0305325443786982249_wp, &
      0.209876543209876543_wp, 0.555555555555555556_wp, 0.84_wp, &
      0.987654320987654321_wp, 0.000678815855557952282_wp, 0.0705661604469038024_wp, &
      0.530476328556042429_wp, 0.927502098733990632_wp, 0.999697683799734036_wp, &
      0.0000194165915287321614_wp, 0.0413476810360825422_wp, 0.432337203021697065_wp, &
      0.801617110760337167_wp, 0.978445191317249505_wp]
   real(wp),parameter::survival(*)=[ &
      0.888611245976936212_wp, 0.704832764699133452_wp, 0.5_wp, &
      0.333333333333333333_wp, 0.155958260754738651_wp, 0.969467455621301775_wp, &
      0.790123456790123457_wp, 0.444444444444444444_wp, 0.16_wp, &
      0.012345679012345679_wp, 0.999321184144442048_wp, 0.929433839553096198_wp, &
      0.469523671443957571_wp, 0.0724979012660093679_wp, 0.000302316200265964077_wp, &
      0.999980583408471268_wp, 0.958652318963917458_wp, 0.567662796978302935_wp, &
      0.198382889239662833_wp, 0.0215548086827504945_wp]
   integer::i

   do i=1,size(x)
      law%d1=a(i);law%d2=b(i)
      call probability_check(law%pdf(x(i)),pdf(i))
      call probability_check(law%cdf(x(i)),cdf(i))
      call probability_check(law%survival(x(i)),survival(i))
      if(pdf(i)>0) call check(law%log_pdf(x(i)),log(pdf(i)))
   end do
   print '(a,i0)', 'Independent distribution reference cases: ',size(x)

   print '(a)', 'PASS fstats-f-positive-tails-reference'
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
