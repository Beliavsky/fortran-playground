program demo_word_counts
   use, intrinsic :: iso_fortran_env, only: int32
   use maps, only: char_to_int32_map_type
   implicit none
   type(char_to_int32_map_type) :: counts
   character(7), parameter :: words(*) = [character(7) :: 'Fortran', 'code', 'Fortran', 'maps', 'code', 'Fortran']
   integer :: i

   call counts%initialize()
   do i = 1, size(words)
      if (counts%contains(trim(words(i)))) then
         call counts%replace(trim(words(i)), counts%get(trim(words(i))) + 1_int32)
      else
         call counts%put(trim(words(i)), 1_int32)
      end if
   end do
   if (counts%get('Fortran') /= 3 .or. counts%get('code') /= 2 .or. counts%get('maps') /= 1) &
      error stop 'word counts'
   if (counts%entries() /= 3) error stop 'distinct words'
   if (counts%contains('absent')) error stop 'missing key'
   print '(a, i3)', 'Fortran: ', counts%get('Fortran')
   print '(a, i3)', 'code:    ', counts%get('code')
   print '(a, i3)', 'maps:    ', counts%get('maps')
   call counts%remove_key('maps')
   if (counts%contains('maps') .or. counts%entries() /= 2) error stop 'remove key'
   call counts%finalize()
   print '(a)', 'PASS maps'
end program demo_word_counts
