! Independent MIT consumer; see licenses/statistics-services-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64,int64
   use ieee_arithmetic, only: ieee_is_finite
   use fortime, only: timer
   implicit none
   type(timer) :: wall,cpu
   integer(int64) :: outer0,inner0,inner1,outer1,rate,total,i,n
   real(real64) :: cpu0,cpu1,cpu2,cpu3,lo,hi,measured,slack
   integer :: t
   call system_clock(count_rate=rate)
   if(rate<=0) error stop 'Clock unavailable'
   do t=1,16
      call system_clock(outer0)
      call cpu_time(cpu0)
      call wall%timer_start()
      call cpu%ctimer_start()
      call system_clock(inner0)
      call cpu_time(cpu1)
      n=10000*t
      total=0
      do i=1,n
         total=total+i
      end do
      call cpu_time(cpu2)
      call system_clock(inner1)
      call cpu%ctimer_stop(nloops=t,print=.false.)
      call wall%timer_stop(nloops=t,print=.false.)
      call cpu_time(cpu3)
      call system_clock(outer1)
      if(total/=n*(n+1)/2) error stop 'Work checksum'
      measured=wall%elapsed_time*t
      slack=4._real64/real(rate,real64)
      lo=real(inner1-inner0,real64)/real(rate,real64)
      hi=real(outer1-outer0,real64)/real(rate,real64)
      if(.not.ieee_is_finite(measured).or.measured<0) error stop 'Wall value'
      if(measured<lo-slack.or.measured>hi+slack) error stop 'Wall bracket'
      measured=cpu%cpu_time*t
      if(.not.ieee_is_finite(measured).or.measured<0) error stop 'CPU value'
      if(measured<cpu2-cpu1-2.e-6_real64.or.measured>cpu3-cpu0+2.e-6_real64) error stop 'CPU bracket'
   end do
   print '(a)', '16 reused wall/CPU timer pairs; averaging, native inner/outer brackets and exact work checksums'
   print '(a)', 'PASS timer-brackets-reference'
end program
