program main
   use string_utf_8, only: char_utf, chars_array, chars, substr, indexof, str_replace_all
   implicit none
   type(char_utf), allocatable :: text(:), replaced(:)

   ! UTF-8 code points, not bytes or combined grapheme clusters.
   text = chars_array('café été')
   if (size(text) /= 8) error stop 'code point count'
   if (chars(text) /= 'café été') error stop 'round trip'
   if (chars(substr(text, 6, 3)) /= 'été') error stop 'substring'
   if (indexof(text, chars_array('é')) /= 4) error stop 'search'
   replaced = str_replace_all(text, chars_array('é'), chars_array('e'))
   if (chars(replaced) /= 'cafe ete') error stop 'replacement'
   print '(a)', 'Original: '//chars(text)
   print '(a,i0)', 'Unicode code points: ', size(text)
   print '(a)', 'Substring: '//chars(substr(text, 6, 3))
   print '(a)', 'Replaced: '//chars(replaced)
   print '(a)', 'PASS string-utf-8'
end program main
