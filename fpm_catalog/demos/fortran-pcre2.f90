program demo_pcre2
   use pcre2
   implicit none(type, external)
   character(*), parameter :: pattern = '(?<year>[0-9]{4})-(?<month>[0-9]{2})-(?<day>[0-9]{2})'
   character(*), parameter :: subject = 'Observation date: 2026-10-27'
   type(c_ptr) :: regex, matches, pointer
   integer :: error_code, status
   integer(pcre2_size) :: error_offset
   integer(pcre2_size), pointer :: offsets(:)
   character(4) :: year
   character(2) :: month, day

   regex = pcre2_compile(pattern, len(pattern,kind=pcre2_size), 0, error_code, error_offset, c_null_ptr)
   if (.not. c_associated(regex)) error stop 'Regular-expression compilation failed'
   matches = pcre2_match_data_create(4, c_null_ptr)
   if (.not. c_associated(matches)) error stop 'Match-data allocation failed'
   status = pcre2_match(regex, subject, len(subject,kind=pcre2_size), &
      0_pcre2_size, 0, matches, c_null_ptr)
   if (status /= 4) error stop 'Expected complete match and three capture groups'
   pointer = pcre2_get_ovector_pointer(matches)
   if (.not. c_associated(pointer)) error stop 'Missing capture offsets'
   call c_f_pointer(pointer, offsets, [8])
   if (any(offsets > len(subject))) error stop 'Capture outside subject'
   year = subject(offsets(3)+1:offsets(4))
   month = subject(offsets(5)+1:offsets(6))
   day = subject(offsets(7)+1:offsets(8))
   if (year /= '2026' .or. month /= '10' .or. day /= '27') error stop 'Incorrect captured date'
   print '(a)', subject
   print '(a)', 'Captured year='//year//', month='//month//', day='//day
   status = pcre2_match(regex, 'No date here', 12_pcre2_size, 0_pcre2_size, 0, matches, c_null_ptr)
   if (status /= PCRE2_ERROR_NOMATCH) error stop 'Expected no match'
   call pcre2_match_data_free(matches)
   call pcre2_code_free(regex)
   print *, 'PASS fortran-pcre2'
end program demo_pcre2
