! Advance across a leap-year day and check the resulting calendar date.
program demo
   use datetime_module
   implicit none
   type(datetime) :: start, finish
   start = datetime(2024, 2, 28)
   finish = start + timedelta(days=2)
   if (finish%getYear() /= 2024 .or. finish%getMonth() /= 3 .or. finish%getDay() /= 1) &
      error stop 'incorrect calendar arithmetic'
   print '(a,a)', 'PASS datetime date=', finish%isoformat()
end program demo
