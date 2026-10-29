program main
   use iso_fortran_env, only: real64
   use ieee_arithmetic, only: ieee_is_finite
   use fortime, only: timer
   implicit none
   type(timer) :: wall, cpu
   integer :: i
   real(real64) :: total, expected

   call wall%timer_start()
   call cpu%ctimer_start()
   total = 0.0_real64
   do i = 1, 100000
      total = total + real(i, real64)
   end do
   call cpu%ctimer_stop(message='CPU seconds:')
   call wall%timer_stop(message='Wall seconds:')
   expected = 100000.0_real64 * 100001.0_real64 / 2
   if (total /= expected) error stop 'sum'
   if (.not. ieee_is_finite(wall%elapsed_time)) error stop 'wall time'
   if (.not. ieee_is_finite(cpu%cpu_time)) error stop 'CPU time'
   if (wall%elapsed_time < 0 .or. cpu%cpu_time < 0) error stop 'negative time'
   print '(a,f16.0)', 'Sum of integers 1 through 100000: ', total
   print '(a)', 'Timings illustrate the API; shared sandbox timings vary.'
   print '(a)', 'PASS fortime'
end program main
