program main
   use utf8, only: utf8_string,construct_utf8_string,utf8_len,utf8_at
   implicit none
   type(utf8_string) :: text
   integer :: i
   call construct_utf8_string(text,'猫 café')
   if (utf8_len(text)/=6) error stop 'Incorrect character count'
   if (utf8_at(text,1)/='猫'.or.utf8_at(text,6)/='é') error stop
   print '(a)', 'Text: 猫 café'
   print '(a,i0)', 'Characters: ',utf8_len(text)
   do i=1,utf8_len(text)
      print '(i3,2x,a)', i,utf8_at(text,i)
   end do
   print *, 'PASS utf8-f'
end program
