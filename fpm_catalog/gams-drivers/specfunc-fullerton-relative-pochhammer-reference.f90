! Independent MIT consumer; see licenses/gamma-relative-ten-drivers-MIT.txt.
program main
   use iso_fortran_env,only:wp=>real64
   use ieee_arithmetic,only:ieee_is_finite
   use specfunc_fullerton,only:poch1
   implicit none
   real(wp),parameter::aa(*)=[ &
      0.5_wp, 0.5_wp, 0.5_wp, &
      0.5_wp, 0.5_wp, 0.5_wp, &
      0.5_wp, 1.5_wp, 1.5_wp, &
      1.5_wp, 1.5_wp, 1.5_wp, &
      1.5_wp, 1.5_wp, 2.0_wp, &
      2.0_wp, 2.0_wp, 2.0_wp, &
      2.0_wp, 2.0_wp, 2.0_wp, &
      4.0_wp, 4.0_wp, 4.0_wp, &
      4.0_wp, 4.0_wp, 4.0_wp, &
      4.0_wp, 8.0_wp, 8.0_wp, &
      8.0_wp, 8.0_wp, 8.0_wp, &
      8.0_wp, 8.0_wp]
   real(wp),parameter::xx(*)=[ &
      -0.125_wp, -1.52587890625e-05_wp, 0.0_wp, &
      1.52587890625e-05_wp, 0.125_wp, 0.5_wp, &
      1.0_wp, -0.125_wp, -1.52587890625e-05_wp, &
      0.0_wp, 1.52587890625e-05_wp, 0.125_wp, &
      0.5_wp, 1.0_wp, -0.125_wp, &
      -1.52587890625e-05_wp, 0.0_wp, 1.52587890625e-05_wp, &
      0.125_wp, 0.5_wp, 1.0_wp, &
      -0.125_wp, -1.52587890625e-05_wp, 0.0_wp, &
      1.52587890625e-05_wp, 0.125_wp, 0.5_wp, &
      1.0_wp, -0.125_wp, -1.52587890625e-05_wp, &
      0.0_wp, 1.52587890625e-05_wp, 0.125_wp, &
      0.5_wp, 1.0_wp]
   real(wp),parameter::expected(*)=[ &
      -2.6990032297002759_wp, -1.96357709180039048_wp, -1.96351002602142348_wp, &
      -1.96344296439207739_wp, -1.52527526803505367_wp, -0.871620832904487426_wp, &
      -0.5_wp, -0.0242524222752069265_wp, 0.0364828318169129991_wp, &
      0.0364899739785765206_wp, 0.0364971160838627922_wp, 0.0934059149561829127_wp, &
      0.256758334191025148_wp, 0.5_wp, 0.372433498039721341_wp, &
      0.422778050932731075_wp, 0.422784335098467139_wp, 0.422790619302190417_wp, &
      0.475684298647313393_wp, 0.658680776358274041_wp, 1.0_wp, &
      1.14710822089506214_wp, 1.25610346525004374_wp, 1.25611766843180047_wp, &
      1.25613187184417188_wp, 1.38064017428413592_wp, 1.87724279885581631_wp, &
      3.0_wp, 1.77525610757754557_wp, 2.01560946576440447_wp, &
      2.01564147795561_wp, 2.01567349084348667_wp, 2.30295909864658187_wp, &
      3.56920924344579865_wp, 7.0_wp]
   integer,parameter::orders(*)=[ &
      0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0, &
      0,0,0,0,0,0,0,0,0,0]
   real(wp)::actual,error,maximum_error
   real::logvalue,sgn
   integer::i
   maximum_error=0
   do i=1,size(expected)
      actual=real(poch1(real(aa(i)),real(xx(i))),wp)
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
   print '(a)', 'PASS specfunc-fullerton-relative-pochhammer-reference'
end program
