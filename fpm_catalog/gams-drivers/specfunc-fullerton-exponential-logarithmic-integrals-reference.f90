! Independent MIT consumer; see licenses/fullerton-functions-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: wp=>real64
   use ieee_arithmetic, only: ieee_is_finite
   use specfunc_fullerton, only: &
      integral_ei, integral_li
   implicit none
   real(wp),parameter :: inputs(*)=[ &
      -16.0_wp, -8.0_wp, -4.0_wp, -2.0_wp, -1.0_wp, -0.5_wp, -0.125_wp, 0.125_wp, 0.375_wp, 0.5_wp, 1.0_wp, 2.0_wp, &
      4.0_wp, 8.0_wp, 16.0_wp, 0.125_wp, 0.5_wp, 0.75_wp, 0.875_wp, 1.125_wp, 1.5_wp, 2.0_wp, 4.0_wp, 8.0_wp, &
      16.0_wp]
   real(wp),parameter :: references(*)=[ &
      -6.64048724944104279e-9_wp, -0.0000376656228439249018_wp, -0.00377935240984890648_wp, &
      -0.0489005107080611196_wp, -0.219383934395520274_wp, -0.559773594776160812_wp, -1.62342564058416879_wp, &
      -1.37320852494298334_wp, 0.00969137720934199948_wp, 0.45421990486317358_wp, 1.89511781635593676_wp, &
      4.95423435600189016_wp, 19.63087447005622_wp, 440.379899534838269_wp, 595560.998670837002_wp, &
      -0.0438315544340059198_wp, -0.378671043061087977_wp, -0.936930011012645492_wp, -1.56540578019534512_wp, &
      -1.44035129627940811_wp, 0.125064986315296356_wp, 1.04516378011749278_wp, 2.96758509503905088_wp, &
      5.25371829955893118_wp, 8.51971646371105908_wp]
   integer,parameter :: which(*)=[ &
      1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,2,2,2,2,2,2,2,2,2]
   integer,parameter :: orders(*)=[ &
      0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
   real(wp) :: actual,expected,relative_error,maximum_error
   integer :: i
   maximum_error=0
   do i=1,size(inputs)
      select case(which(i))
      case(1)
         actual=real(integral_ei(real(inputs(i))),wp)
      case(2)
         actual=real(integral_li(real(inputs(i))),wp)
      case default
         error stop 'Unknown function selector'
      end select
      expected=references(i)
      if(.not.ieee_is_finite(actual)) error stop 'Nonfinite special function'
      relative_error=abs(actual-expected)/max(abs(expected),1.e-30_wp)
      if(relative_error>5.e-5_wp) then
         print '(a,i0,a,es16.8,a,es16.8,a,es16.8)', 'Case ',i,': x=',inputs(i), &
            ' actual=',actual,' expected=',expected
         error stop 'Independent high-precision reference'
      end if
      maximum_error=max(maximum_error,relative_error)
   end do
   print '(a,i0)', 'Default REAL32 function comparisons with independent references: ',size(inputs)
   print '(a,es12.4)', 'Maximum relative error (reference floor 1e-30): ',maximum_error
   print '(a)', 'PASS specfunc-fullerton-exponential-logarithmic-integrals-reference'
end program
