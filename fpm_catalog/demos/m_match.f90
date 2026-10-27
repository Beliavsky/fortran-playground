program main
   use M_match, only: getpat, match, regex_pattern, YES, ERR
   implicit none
   type(regex_pattern) :: pattern
   integer :: status
   status = getpat('^[0-9][0-9]*$', pattern%pat)
   if (status == ERR) error stop 'invalid pattern'
   if (match('2026'//char(10), pattern%pat) /= YES) error stop 'digits not matched'
   if (match('abc'//char(10), pattern%pat) == YES) error stop 'letters matched as digits'
   print *, 'Matched digits and rejected letters.'
   print *, 'PASS m_match'
end program
