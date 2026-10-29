program main
   use fregex, only: regex_t, match_t
   implicit none
   type(regex_t) :: expression
   type(match_t) :: first
   integer :: status
   call expression%compile('([A-Za-z]+)=(-?[0-9]+[.][0-9]+)', flags=[0], info=status)
   if (status /= 0) error stop 'compile pattern'
   call expression%match('temp=23.50 pressure=-1.25', flags=[0], info=status)
   if (status /= 0) error stop 'match status'
   if (.not. allocated(expression%matches)) error stop 'no matches'
   if (size(expression%matches) /= 2) error stop 'match count'
   first = expression%matches(1)
   if (size(first%groups) /= 2) error stop 'group count'
   if (first%groups(1)%content /= 'temp') error stop 'name capture'
   if (first%groups(2)%content /= '23.50') error stop 'first number'
   if (expression%matches(2)%groups(2)%content /= '-1.25') error stop 'second number'
   print *, first%groups(1)%content, ': ', first%groups(2)%content
   print *, expression%matches(2)%groups(1)%content, ': ', expression%matches(2)%groups(2)%content
   call expression%free()
   print *, 'PASS fregex'
end program
