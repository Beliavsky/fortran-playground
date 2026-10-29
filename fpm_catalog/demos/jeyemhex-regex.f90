program main
   use regex, only: re_match, re_match_str, re_split, re_replace
   implicit none
   character(8), allocatable :: fields(:)
   character(:), allocatable :: number, replaced
   if (.not. re_match('^temp=\d+\.\d+$', 'temp=23.50')) error stop 'positive match'
   if (re_match('^temp=\d+\.\d+$', 'temp=warm')) error stop 'negative match'
   number = trim(re_match_str('\d+\.\d+', 'temp=23.50 kelvin'))
   if (number /= '23.50') error stop 'matched substring'
   call re_split('\s*,\s*', 'red, green,blue', fields)
   if (size(fields) /= 3) error stop 'split count'
   if (any(fields /= [character(8) :: 'red','green','blue'])) error stop 'split fields'
   replaced = trim(re_replace('temp', 'temperature', 'temp=23.50'))
   if (replaced /= 'temperature=23.50') error stop 'replacement'
   print '(a)', 'Matched number: '//number
   print '(a)', 'Fields: '//trim(fields(1))//', '//trim(fields(2))//', '//trim(fields(3))
   print '(a)', replaced
   print *, 'PASS jeyemhex-regex'
end program
