! Independent MIT consumer; see licenses/fullerton-functions-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: wp=>real64
   use ieee_arithmetic, only: ieee_is_finite
   use specfunc_fullerton, only: &
      integral_si, integral_ci
   implicit none
   real(wp),parameter :: inputs(*)=[ &
      0.00390625_wp, 0.00390625_wp, 0.125_wp, 0.125_wp, 0.5_wp, 0.5_wp, 1.0_wp, 1.0_wp, 2.0_wp, 2.0_wp, 3.0_wp, &
      3.0_wp, 4.0_wp, 4.0_wp, 8.0_wp, 8.0_wp, 16.0_wp, 16.0_wp]
   real(wp),parameter :: references(*)=[ &
      0.00390624668863236164_wp, -4.96796559427286992_wp, 0.124891543904672252_wp, -1.50612958452963966_wp, &
      0.493107418043066689_wp, -0.177784078806612901_wp, 0.946083070367183015_wp, 0.337403922900968135_wp, &
      1.60541297680269485_wp, 0.422980828774864996_wp, 1.84865252799946826_wp, 0.119629786008000328_wp, &
      1.75820313894905306_wp, -0.140981697886930412_wp, 1.57418682170694205_wp, 0.122433882532009557_wp, &
      1.63130226827003289_wp, -0.0142001901201900224_wp]
   integer,parameter :: which(*)=[ &
      1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2]
   integer,parameter :: orders(*)=[ &
      0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
   real(wp) :: actual,expected,relative_error,maximum_error
   integer :: i
   maximum_error=0
   do i=1,size(inputs)
      select case(which(i))
      case(1)
         actual=real(integral_si(real(inputs(i))),wp)
      case(2)
         actual=real(integral_ci(real(inputs(i))),wp)
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
   print '(a)', 'PASS specfunc-fullerton-sine-cosine-integrals-reference'
end program
