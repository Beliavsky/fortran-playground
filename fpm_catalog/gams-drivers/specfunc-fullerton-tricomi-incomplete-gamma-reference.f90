! Independent MIT consumer; see licenses/gamma-relative-ten-drivers-MIT.txt.
program main
   use iso_fortran_env,only:wp=>real64
   use ieee_arithmetic,only:ieee_is_finite
   use specfunc_fullerton,only:gamma_tricomi
   implicit none
   real(wp),parameter::aa(*)=[ &
      0.5_wp, 0.5_wp, 0.5_wp, &
      0.5_wp, 0.5_wp, 0.5_wp, &
      0.5_wp, 1.0_wp, 1.0_wp, &
      1.0_wp, 1.0_wp, 1.0_wp, &
      1.0_wp, 1.0_wp, 1.5_wp, &
      1.5_wp, 1.5_wp, 1.5_wp, &
      1.5_wp, 1.5_wp, 1.5_wp, &
      2.0_wp, 2.0_wp, 2.0_wp, &
      2.0_wp, 2.0_wp, 2.0_wp, &
      2.0_wp, 3.0_wp, 3.0_wp, &
      3.0_wp, 3.0_wp, 3.0_wp, &
      3.0_wp, 3.0_wp, 4.0_wp, &
      4.0_wp, 4.0_wp, 4.0_wp, &
      4.0_wp, 4.0_wp, 4.0_wp, &
      8.0_wp, 8.0_wp, 8.0_wp, &
      8.0_wp, 8.0_wp, 8.0_wp, &
      8.0_wp]
   real(wp),parameter::xx(*)=[ &
      0.0_wp, 0.125_wp, 0.5_wp, &
      1.0_wp, 2.0_wp, 4.0_wp, &
      8.0_wp, 0.0_wp, 0.125_wp, &
      0.5_wp, 1.0_wp, 2.0_wp, &
      4.0_wp, 8.0_wp, 0.0_wp, &
      0.125_wp, 0.5_wp, 1.0_wp, &
      2.0_wp, 4.0_wp, 8.0_wp, &
      0.0_wp, 0.125_wp, 0.5_wp, &
      1.0_wp, 2.0_wp, 4.0_wp, &
      8.0_wp, 0.0_wp, 0.125_wp, &
      0.5_wp, 1.0_wp, 2.0_wp, &
      4.0_wp, 8.0_wp, 0.0_wp, &
      0.125_wp, 0.5_wp, 1.0_wp, &
      2.0_wp, 4.0_wp, 8.0_wp, &
      0.0_wp, 0.125_wp, 0.5_wp, &
      1.0_wp, 2.0_wp, 4.0_wp, &
      8.0_wp]
   real(wp),parameter::expected(*)=[ &
      1.12837916709551257_wp, 1.0830752376761713_wp, 0.965468738669867308_wp, &
      0.842700792949714869_wp, 0.674933236039655047_wp, 0.497661132509476367_wp, &
      0.353530995643404964_wp, 1.0_wp, 0.940024779323236777_wp, &
      0.786938680574733153_wp, 0.632120558828557678_wp, 0.432332358381693654_wp, &
      0.245421090277816455_wp, 0.124958067171512186_wp, 0.752252778063675049_wp, &
      0.698272942187166755_wp, 0.562144356090868484_wp, 0.427593295529120166_wp, &
      0.261111860931245366_wp, 0.119248536788846078_wp, 0.044144058325342582_wp, &
      0.5_wp, 0.460223013909130994_wp, 0.360816041724199458_wp, &
      0.264241117657115357_wp, 0.148498537572540481_wp, 0.0567763628472705687_wp, &
      0.0155778255679512093_wp, 0.166666666666666667_wp, 0.151796500934666338_wp, &
      0.115101423735765493_wp, 0.080301397071394196_wp, 0.0404154479771170676_wp, &
      0.0119046358507258696_wp, 0.00192626178174999417_wp, 0.0416666666666666667_wp, &
      0.0377094706978701697_wp, 0.0280259609006531784_wp, 0.0189881568761538091_wp, &
      0.00892978371884080946_wp, 0.00221300734231754323_wp, 0.000233793917970780275_wp, &
      0.0000248015873015873016_wp, 0.0000221951581008452815_wp, 0.0000159224086111453397_wp, &
      0.0000102491966746416947_wp, 4.28405846819805737e-6_wp, 7.80237057385976242e-7_wp, &
      3.26060766287449309e-8_wp]
   integer,parameter::orders(*)=[ &
      0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0, &
      0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
   real(wp)::actual,error,maximum_error
   real::logvalue,sgn
   integer::i
   maximum_error=0
   do i=1,size(expected)
      actual=real(gamma_tricomi(real(aa(i)),real(xx(i))),wp)
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
   print '(a)', 'PASS specfunc-fullerton-tricomi-incomplete-gamma-reference'
end program
