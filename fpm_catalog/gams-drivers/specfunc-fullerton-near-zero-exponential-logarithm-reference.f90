! Independent MIT consumer; see licenses/fullerton-functions-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: wp=>real64
   use ieee_arithmetic, only: ieee_is_finite
   use specfunc_fullerton, only: &
      lnrel, exprel
   implicit none
   real(wp),parameter :: inputs(*)=[ &
      -0.875_wp, -0.875_wp, -0.5_wp, -0.5_wp, -0.00390625_wp, -0.00390625_wp, -1.52587890625e-05_wp, &
      -1.52587890625e-05_wp, -5.960464477539063e-08_wp, -5.960464477539063e-08_wp, 0.0_wp, 0.0_wp, &
      5.960464477539063e-08_wp, 5.960464477539063e-08_wp, 1.52587890625e-05_wp, 1.52587890625e-05_wp, 0.00390625_wp, &
      0.00390625_wp, 0.3749990463256836_wp, 0.3749990463256836_wp, 0.375_wp, 0.375_wp, 0.3750009536743164_wp, &
      0.3750009536743164_wp, 0.4999990463256836_wp, 0.4999990463256836_wp, 0.5_wp, 0.5_wp, 0.5000009536743164_wp, &
      0.5000009536743164_wp, 1.0_wp, 1.0_wp, 2.0_wp, 2.0_wp, 4.0_wp, 4.0_wp, 8.0_wp, 8.0_wp]
   real(wp),parameter :: references(*)=[ &
      -2.07944154167983593_wp, 0.666443406081704683_wp, -0.693147180559945309_wp, 0.786938680574733153_wp, &
      -0.00391389932113632909_wp, 0.998049415649922544_wp, -0.0000152589054790060784_wp, 0.999992370644273709_wp, &
      -5.9604646551747535e-8_wp, 0.999999970197678204_wp, 0.0_wp, 1.0_wp, 5.96046429990338562e-8_wp, &
      1.00000002980232298_wp, 0.0000152586726483623974_wp, 1.00000762943333651_wp, 0.00389864041565732301_wp, &
      1.0019556706169788_wp, 0.318453037536973065_wp, 1.21330982435556695_wp, 0.318453731118534616_wp, &
      1.21331043898187023_wp, 0.318454424699615111_wp, 1.21331105360857617_wp, 0.405464472325084668_wp, &
      1.29744187138947379_wp, 0.405465108108164382_wp, 1.29744254140025629_wp, 0.405465743890839876_wp, &
      1.29744321141148192_wp, 0.693147180559945309_wp, 1.71828182845904524_wp, 1.09861228866810969_wp, &
      3.19452804946532511_wp, 1.60943791243410037_wp, 13.3995375082860598_wp, 2.19722457733621938_wp, &
      372.494748380216034_wp]
   integer,parameter :: which(*)=[ &
      1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2, &
      1,2,1,2,1,2,1,2]
   integer,parameter :: orders(*)=[ &
      0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0, &
      0,0,0,0,0,0,0,0]
   real(wp) :: actual,expected,relative_error,maximum_error
   integer :: i
   maximum_error=0
   do i=1,size(inputs)
      select case(which(i))
      case(1)
         actual=real(lnrel(real(inputs(i))),wp)
      case(2)
         actual=real(exprel(real(inputs(i))),wp)
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
   print '(a)', 'PASS specfunc-fullerton-near-zero-exponential-logarithm-reference'
end program
