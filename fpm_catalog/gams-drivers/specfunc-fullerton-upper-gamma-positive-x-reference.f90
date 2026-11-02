! Independent MIT consumer; see licenses/gamma-relative-ten-drivers-MIT.txt.
program main
   use iso_fortran_env,only:wp=>real64
   use ieee_arithmetic,only:ieee_is_finite
   use specfunc_fullerton,only:inc_gamma_compl
   implicit none
   real(wp),parameter::aa(*)=[ &
      0.5_wp, 0.5_wp, 0.5_wp, &
      0.5_wp, 0.5_wp, 0.5_wp, &
      1.0_wp, 1.0_wp, 1.0_wp, &
      1.0_wp, 1.0_wp, 1.0_wp, &
      1.5_wp, 1.5_wp, 1.5_wp, &
      1.5_wp, 1.5_wp, 1.5_wp, &
      2.0_wp, 2.0_wp, 2.0_wp, &
      2.0_wp, 2.0_wp, 2.0_wp, &
      3.0_wp, 3.0_wp, 3.0_wp, &
      3.0_wp, 3.0_wp, 3.0_wp, &
      4.0_wp, 4.0_wp, 4.0_wp, &
      4.0_wp, 4.0_wp, 4.0_wp, &
      8.0_wp, 8.0_wp, 8.0_wp, &
      8.0_wp, 8.0_wp, 8.0_wp, &
      -2.0_wp, -2.0_wp, -2.0_wp, &
      -2.0_wp, -2.0_wp, -2.0_wp, &
      -1.0_wp, -1.0_wp, -1.0_wp, &
      -1.0_wp, -1.0_wp, -1.0_wp, &
      -0.5_wp, -0.5_wp, -0.5_wp, &
      -0.5_wp, -0.5_wp, -0.5_wp, &
      0.0_wp, 0.0_wp, 0.0_wp, &
      0.0_wp, 0.0_wp, 0.0_wp]
   real(wp),parameter::xx(*)=[ &
      0.125_wp, 0.5_wp, 1.0_wp, &
      2.0_wp, 4.0_wp, 8.0_wp, &
      0.125_wp, 0.5_wp, 1.0_wp, &
      2.0_wp, 4.0_wp, 8.0_wp, &
      0.125_wp, 0.5_wp, 1.0_wp, &
      2.0_wp, 4.0_wp, 8.0_wp, &
      0.125_wp, 0.5_wp, 1.0_wp, &
      2.0_wp, 4.0_wp, 8.0_wp, &
      0.125_wp, 0.5_wp, 1.0_wp, &
      2.0_wp, 4.0_wp, 8.0_wp, &
      0.125_wp, 0.5_wp, 1.0_wp, &
      2.0_wp, 4.0_wp, 8.0_wp, &
      0.125_wp, 0.5_wp, 1.0_wp, &
      2.0_wp, 4.0_wp, 8.0_wp, &
      0.125_wp, 0.5_wp, 1.0_wp, &
      2.0_wp, 4.0_wp, 8.0_wp, &
      0.125_wp, 0.5_wp, 1.0_wp, &
      2.0_wp, 4.0_wp, 8.0_wp, &
      0.125_wp, 0.5_wp, 1.0_wp, &
      2.0_wp, 4.0_wp, 8.0_wp, &
      0.125_wp, 0.5_wp, 1.0_wp, &
      2.0_wp, 4.0_wp, 8.0_wp]
   real(wp),parameter::expected(*)=[ &
      1.09373709732757051_wp, 0.562418231594407124_wp, 0.278805585280661976_wp, &
      0.0806471179603176908_wp, 0.00829106938067266736_wp, 0.000112271629100146558_wp, &
      0.882496902584595403_wp, 0.606530659712633424_wp, 0.367879441171442322_wp, &
      0.135335283236612692_wp, 0.0183156388887341803_wp, 0.000335462627902511839_wp, &
      0.85887832076063098_wp, 0.71009105827755696_wp, 0.50728223381177331_wp, &
      0.231716552000980693_wp, 0.0407768124678046943_wp, 0.00100496741064817588_wp, &
      0.992809015407669828_wp, 0.909795989568950135_wp, 0.735758882342884643_wp, &
      0.406005849709838076_wp, 0.0915781944436709015_wp, 0.00301916365112260655_wp, &
      1.99940704491822396_wp, 1.97122464406605863_wp, 1.83939720585721161_wp, &
      1.35335283236612692_wp, 0.476206611107088688_wp, 0.0275079354880059708_wp, &
      5.99994476151753242_wp, 5.98949026466225506_wp, 5.88607105874307715_wp, &
      5.14274076299128229_wp, 2.6008207222002536_wp, 0.254280671950103974_wp, &
      5039.99999999333241_wp, 5039.99968652758047_wp, 5039.94834404875981_wp, &
      5034.47253640199214_wp, 4782.28657640404941_wp, 2282.92247981445221_wp, &
      25.5216260926607557_wp, 0.886417457100713829_wp, 0.109691967197760137_wp, &
      0.0075333449494539733_wp, 0.000172585059105623837_wp, 4.87198958543834701e-7_wp, &
      5.43654958009259443_wp, 0.653287724649106035_wp, 0.148495506775922048_wp, &
      0.0187671309102452264_wp, 0.000799557312334638595_wp, 4.26720564388907808e-6_wp, &
      2.80468215889439056_wp, 0.590691306732599344_wp, 0.17814771178156069_wp, &
      0.0300987571001864663_wp, 0.00173350012738884557_wp, 0.0000126646408242325348_wp, &
      1.62342564058416879_wp, 0.559773594776160812_wp, 0.219383934395520274_wp, &
      0.0489005107080611196_wp, 0.00377935240984890648_wp, 0.0000376656228439249018_wp]
   integer,parameter::orders(*)=[ &
      0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0, &
      0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0, &
      0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
   real(wp)::actual,error,maximum_error
   real::logvalue,sgn
   integer::i
   maximum_error=0
   do i=1,size(expected)
      actual=real(inc_gamma_compl(real(aa(i)),real(xx(i))),wp)
      if(.not.ieee_is_finite(actual)) error stop 'Nonfinite result'
      error=abs(actual-expected(i))/max(abs(expected(i)),1.e-30_wp)
      if(error>5.e-5_wp) then
         print *, 'Case, a, x, n, actual, reference:',i,aa(i),xx(i),orders(i),actual,expected(i)
         error stop 'Independent high precision reference'
      end if
      maximum_error=max(maximum_error,error)
   end do
   print '(a,i0)', 'Default REAL32 comparisons with independent high precision references: ',size(expected)
   print '(a,es12.4)', 'Maximum relative error (reference floor 1e-30): ',maximum_error
   print '(a)', 'PASS specfunc-fullerton-upper-gamma-positive-x-reference'
end program
