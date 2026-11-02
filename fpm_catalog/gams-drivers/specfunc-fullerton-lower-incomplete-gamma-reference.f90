! Independent MIT consumer; see licenses/gamma-relative-ten-drivers-MIT.txt.
program main
   use iso_fortran_env,only:wp=>real64
   use ieee_arithmetic,only:ieee_is_finite
   use specfunc_fullerton,only:inc_gamma
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
      0.0_wp, 0.678716753577945516_wp, 1.2100356193111089_wp, &
      1.49364826562485405_wp, 1.69180673294519834_wp, 1.76416278152484336_wp, &
      1.77234157927641588_wp, 0.0_wp, 0.117503097415404597_wp, &
      0.393469340287366576_wp, 0.632120558828557678_wp, 0.864664716763387308_wp, &
      0.98168436111126582_wp, 0.999664537372097488_wp, 0.0_wp, &
      0.0273486046921270338_wp, 0.176135867175201053_wp, 0.378944691640984704_wp, &
      0.65451037345177732_wp, 0.845450112984953319_wp, 0.885221958042109838_wp, &
      0.0_wp, 0.00719098459233017178_wp, 0.0902040104310498646_wp, &
      0.264241117657115357_wp, 0.593994150290161924_wp, 0.908421805556329099_wp, &
      0.996980836348877393_wp, 0.0_wp, 0.000592955081776040384_wp, &
      0.0287753559339413733_wp, 0.160602794142788392_wp, 0.646647167633873081_wp, &
      1.52379338889291131_wp, 1.97249206451199403_wp, 0.0_wp, &
      0.0000552384824675832565_wp, 0.0105097353377449419_wp, 0.113928941256922854_wp, &
      0.857259237008717708_wp, 3.3991792777997464_wp, 5.74571932804989603_wp, &
      0.0_wp, 6.66758995224596374e-9_wp, 0.000313472419531923874_wp, &
      0.0516559512401941413_wp, 5.52746359800786154_wp, 257.713423595950589_wp, &
      2757.07752018554779_wp]
   integer,parameter::orders(*)=[ &
      0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0, &
      0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
   real(wp)::actual,error,maximum_error
   real::logvalue,sgn
   integer::i
   maximum_error=0
   do i=1,size(expected)
      actual=real(inc_gamma(real(aa(i)),real(xx(i))),wp)
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
   print '(a)', 'PASS specfunc-fullerton-lower-incomplete-gamma-reference'
end program
