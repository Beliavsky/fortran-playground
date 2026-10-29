program main
   use time_f, only: tm, time_t, gmtime, strftime, difftime
   implicit none
   type(tm) :: date
   integer(time_t), parameter :: epoch = 0_time_t
   character(32) :: text
   integer :: length
   date = gmtime(epoch)
   if (date%tm_year /= 70 .or. date%tm_mon /= 0 .or. date%tm_mday /= 1) &
      error stop 'UTC epoch date'
   text = ' '
   ! The actual allocation is large enough even if the wrapper ignores maxsize.
   length = strftime(text, 5, '%Y-%m-%d %H:%M:%S', date)
   if (length /= 0) error stop 'strftime ignored the supplied buffer limit'
   length = strftime(text, len(text), '%Y-%m-%d %H:%M:%S', date)
   if (length /= 19) error stop 'format length'
   if (text(:length) /= '1970-01-01 00:00:00') error stop 'formatted UTC date'
   if (abs(difftime(86400_time_t, epoch)-86400.0d0) > 1.0d-9) error stop 'elapsed seconds'
   print '(a)', text(:length)
   print *, 'PASS time-f'
end program
