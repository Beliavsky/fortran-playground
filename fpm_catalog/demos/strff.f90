program demo_strff
   use strff, only: split_at, join, to_string, operator(.includes.), operator(.startswith.)
   use iso_varying_string, only: varying_string, char
   implicit none
   type(varying_string), allocatable :: words(:)
   character(:), allocatable :: combined
   integer :: i

   words = split_at('red,green,blue', ',')
   if (size(words) /= 3) error stop 'Incorrect token count'
   if (char(words(1)) /= 'red' .or. char(words(2)) /= 'green' .or. char(words(3)) /= 'blue') &
      error stop 'Incorrect split result'
   combined = char(join(words, ' | '))
   if (combined /= 'red | green | blue') error stop 'Incorrect joined text'
   if (.not. (combined .includes. 'green')) error stop 'Substring check failed'
   if (.not. (combined .startswith. 'red')) error stop 'Prefix check failed'
   if (char(to_string(42)) /= '42') error stop 'Integer-to-string check failed'
   print '(a)', combined
   do i = 1, size(words)
      print '(a)', 'Word '//char(to_string(i))//': '//char(words(i))
   end do
   print *, 'PASS strff'
end program demo_strff
