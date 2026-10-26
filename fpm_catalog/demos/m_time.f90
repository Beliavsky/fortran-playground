program main
   use M_time, only: d2j, realtime
   implicit none
   real(realtime) :: julian
   ! DATE_AND_TIME convention: year, month, day, UTC offset, hour, minute, second, millisecond.
   julian = d2j([2000,1,1,0,12,0,0,0])
   if (abs(julian-2451545.0_realtime) > 1.e-8_realtime) error stop 'incorrect Julian day'
   print *, 'Julian date of noon on 2000-01-01:', julian
   print *, 'PASS m_time'
end program main
