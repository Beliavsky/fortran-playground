! Independent MIT consumer; see licenses/special-functions-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64, int64
   use ieee_arithmetic, only: ieee_is_finite
   use stdlib_specialfunctions_gamma, only: gamma
   implicit none
   complex(real64),parameter :: z(24) = [ &
      cmplx(-1.25_real64,-1.25_real64,kind=real64), &
      cmplx(-1.25_real64,-0.25_real64,kind=real64), &
      cmplx(-1.25_real64,0.25_real64,kind=real64), &
      cmplx(-1.25_real64,1.25_real64,kind=real64), &
      cmplx(-0.25_real64,-1.25_real64,kind=real64), &
      cmplx(-0.25_real64,-0.25_real64,kind=real64), &
      cmplx(-0.25_real64,0.25_real64,kind=real64), &
      cmplx(-0.25_real64,1.25_real64,kind=real64), &
      cmplx(0.25_real64,-1.25_real64,kind=real64), &
      cmplx(0.25_real64,-0.25_real64,kind=real64), &
      cmplx(0.25_real64,0.25_real64,kind=real64), &
      cmplx(0.25_real64,1.25_real64,kind=real64), &
      cmplx(0.75_real64,-1.25_real64,kind=real64), &
      cmplx(0.75_real64,-0.25_real64,kind=real64), &
      cmplx(0.75_real64,0.25_real64,kind=real64), &
      cmplx(0.75_real64,1.25_real64,kind=real64), &
      cmplx(1.5_real64,-1.25_real64,kind=real64), &
      cmplx(1.5_real64,-0.25_real64,kind=real64), &
      cmplx(1.5_real64,0.25_real64,kind=real64), &
      cmplx(1.5_real64,1.25_real64,kind=real64), &
      cmplx(3.5_real64,-1.25_real64,kind=real64), &
      cmplx(3.5_real64,-0.25_real64,kind=real64), &
      cmplx(3.5_real64,0.25_real64,kind=real64), &
      cmplx(3.5_real64,1.25_real64,kind=real64) ]
   complex(real64),parameter :: expected(24) = [ &
      cmplx(-0.0029304086738972725694716356_real64,-0.16412590934330116863553978_real64,kind=real64), &
      cmplx(1.8864540205635624573533301_real64,-1.6691601293439379450691692_real64,kind=real64), &
      cmplx(1.8864540205635624573533301_real64,1.6691601293439379450691692_real64,kind=real64), &
      cmplx(-0.0029304086738972725694716356_real64,0.16412590934330116863553978_real64,kind=real64), &
      cmplx(-0.20149437583675487008258519_real64,0.20882039752149805150626427_real64,kind=real64), &
      cmplx(-2.775357558040437557958955_real64,1.614836656539031816998129_real64,kind=real64), &
      cmplx(-2.775357558040437557958955_real64,-1.614836656539031816998129_real64,kind=real64), &
      cmplx(-0.20149437583675487008258519_real64,-0.20882039752149805150626427_real64,kind=real64), &
      cmplx(0.071608186350694685230878605_real64,0.32691508002793578820688281_real64,kind=real64), &
      cmplx(1.6511332803889208011144274_real64,1.8378758749947889649011368_real64,kind=real64), &
      cmplx(1.6511332803889208011144274_real64,-1.8378758749947889649011368_real64,kind=real64), &
      cmplx(0.071608186350694685230878605_real64,-0.32691508002793578820688281_real64,kind=real64), &
      cmplx(0.31139909086106128190347664_real64,0.19966287041556907472666541_real64,kind=real64), &
      cmplx(1.097548553644867343739271_real64,0.29013022537535143524020649_real64,kind=real64), &
      cmplx(1.097548553644867343739271_real64,-0.29013022537535143524020649_real64,kind=real64), &
      cmplx(0.31139909086106128190347664_real64,-0.19966287041556907472666541_real64,kind=real64), &
      cmplx(0.45838153887109250398622869_real64,-0.11908398993537923368879323_real64,kind=real64), &
      cmplx(0.86085217993425804214503547_real64,-0.0096876301173166840757145785_real64,kind=real64), &
      cmplx(0.86085217993425804214503547_real64,0.0096876301173166840757145785_real64,kind=real64), &
      cmplx(0.45838153887109250398622869_real64,0.11908398993537923368879323_real64,kind=real64), &
      cmplx(0.4072896666036186840259091_real64,-2.5524039223391045936253787_real64,kind=real64), &
      cmplx(3.1647047833902598463341037_real64,-0.89657531599186331467423298_real64,kind=real64), &
      cmplx(3.1647047833902598463341037_real64,0.89657531599186331467423298_real64,kind=real64), &
      cmplx(0.4072896666036186840259091_real64,2.5524039223391045936253787_real64,kind=real64) ]
   complex(real64) :: actual
   integer :: j
   do j=1,size(z)
      actual=gamma(z(j))
      if(.not.ieee_is_finite(real(actual,real64)).or..not.ieee_is_finite(aimag(actual))) &
         error stop 'Nonfinite complex result'
      if(abs(actual-expected(j))>2.e-11_real64*max(1._real64,abs(expected(j)))) then
         print *, 'argument, actual, expected: ',z(j),actual,expected(j)
         error stop 'Independent complex reference'
      end if
   end do
   print '(a)', '24 complex references from independent 80/120-digit mpmath evaluations'
   print '(a)', 'PASS stdlib-complex-gamma-reference'

end program
