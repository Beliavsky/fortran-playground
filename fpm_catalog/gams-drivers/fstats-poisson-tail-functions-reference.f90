! Independent MIT consumer; see licenses/fstats-summaries-ten-drivers-MIT.txt.
program main
   use iso_fortran_env,only:wp=>real64
   use ieee_arithmetic,only:ieee_is_finite
   use fstats_poisson_distribution,only: &
      poisson_distribution
   implicit none
   type(poisson_distribution)::law
   real(wp),parameter::a(*)=[ &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.125_wp, 0.125_wp, &
      0.125_wp, 0.125_wp, 0.125_wp, &
      0.125_wp, 0.125_wp, 0.5_wp, &
      0.5_wp, 0.5_wp, 0.5_wp, &
      0.5_wp, 0.5_wp, 0.5_wp, &
      2.0_wp, 2.0_wp, 2.0_wp, &
      2.0_wp, 2.0_wp, 2.0_wp, &
      2.0_wp, 8.0_wp, 8.0_wp, &
      8.0_wp, 8.0_wp, 8.0_wp, &
      8.0_wp, 8.0_wp]
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
      0.0_wp, 0.0_wp]
   real(wp),parameter::x(*)=[ &
      -1.0_wp, 0.0_wp, 1.0_wp, &
      2.0_wp, 4.0_wp, 8.0_wp, &
      12.0_wp, -1.0_wp, 0.0_wp, &
      1.0_wp, 2.0_wp, 4.0_wp, &
      8.0_wp, 12.0_wp, -1.0_wp, &
      0.0_wp, 1.0_wp, 2.0_wp, &
      4.0_wp, 8.0_wp, 12.0_wp, &
      -1.0_wp, 0.0_wp, 1.0_wp, &
      2.0_wp, 4.0_wp, 8.0_wp, &
      12.0_wp, -1.0_wp, 0.0_wp, &
      1.0_wp, 2.0_wp, 4.0_wp, &
      8.0_wp, 12.0_wp]
   real(wp),parameter::pdf(*)=[ &
      0.0_wp, 1.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.882496902584595403_wp, &
      0.110312112823074425_wp, 0.00689450705144215158_wp, 8.97722272323196821e-6_wp, &
      1.30458617048455639e-12_wp, 2.68099733188936154e-20_wp, 0.0_wp, &
      0.606530659712633424_wp, 0.303265329856316712_wp, 0.075816332464079178_wp, &
      0.00157950692633498287_wp, 5.8761418390438351e-8_wp, 3.09140458703905466e-13_wp, &
      0.0_wp, 0.135335283236612692_wp, 0.270670566473225384_wp, &
      0.270670566473225384_wp, 0.0902235221577417946_wp, 0.000859271639597540901_wp, &
      1.15726820147816956e-6_wp, 0.0_wp, 0.000335462627902511839_wp, &
      0.00268370102322009471_wp, 0.0107348040928803788_wp, 0.0572522884953620205_wp, &
      0.139586531950596926_wp, 0.0481268042819566506_wp]
   real(wp),parameter::cdf(*)=[ &
      0.0_wp, 1.0_wp, 1.0_wp, &
      1.0_wp, 1.0_wp, 1.0_wp, &
      1.0_wp, 0.0_wp, 0.882496902584595403_wp, &
      0.992809015407669828_wp, 0.99970352245911198_wp, 0.999999770808978635_wp, &
      0.999999999999981652_wp, 1.0_wp, 0.0_wp, &
      0.606530659712633424_wp, 0.909795989568950135_wp, 0.985612322033029313_wp, &
      0.999827884370044159_wp, 0.999999996564509753_wp, 0.999999999999987671_wp, &
      0.0_wp, 0.135335283236612692_wp, 0.406005849709838076_wp, &
      0.676676416183063459_wp, 0.947346982656288843_wp, 0.999762552671738838_wp, &
      0.999999792653041863_wp, 0.0_wp, 0.000335462627902511839_wp, &
      0.00301916365112260655_wp, 0.0137539677440029854_wp, 0.0996324004870460161_wp, &
      0.592547341437591412_wp, 0.93620280326343812_wp]
   real(wp),parameter::survival(*)=[ &
      1.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 1.0_wp, 0.117503097415404597_wp, &
      0.00719098459233017178_wp, 0.000296477540888020192_wp, 2.29191021365241201e-7_wp, &
      1.8348343849960224e-14_wp, 2.60109217019584017e-22_wp, 1.0_wp, &
      0.393469340287366576_wp, 0.0902040104310498646_wp, 0.0143876779669706866_wp, &
      0.000172115629955840778_wp, 3.43549024684813206e-9_wp, 1.23292716306129811e-14_wp, &
      1.0_wp, 0.864664716763387308_wp, 0.593994150290161924_wp, &
      0.323323583816936541_wp, 0.0526530173437111567_wp, 0.000237447328261161786_wp, &
      2.07346958137025711e-7_wp, 1.0_wp, 0.999664537372097488_wp, &
      0.996980836348877393_wp, 0.986246032255997015_wp, 0.900367599512953984_wp, &
      0.407452658562408588_wp, 0.06379719673656188_wp]
   integer::i

   do i=1,size(x)
      law%occrence_rate=a(i)
      call probability_check(law%pdf(x(i)),pdf(i))
      call probability_check(law%cdf(x(i)),cdf(i))
      call probability_check(law%survival(x(i)),survival(i))
      if(pdf(i)>0) call check(law%log_pdf(x(i)),log(pdf(i)))
   end do
   print '(a,i0)', 'Independent distribution reference cases: ',size(x)

   print '(a)', 'PASS fstats-poisson-tail-functions-reference'
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
