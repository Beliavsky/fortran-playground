program demo_binary_strings
   use bstrith, only: add, sub, xor, not, shift_l, shift_r
   implicit none
   character(8) :: bits, expected
   integer :: i, amount

   ! Exhaustively check every eight-bit value, including carry and wraparound.
   do i = 0, 255
      write(bits, '(b8.8)') i
      write(expected, '(b8.8)') modulo(i + 1, 256)
      if (add(bits, '00000001') /= expected) error stop 'addition'
      if (sub(expected, '00000001') /= bits) error stop 'subtraction round trip'
      if (xor(bits, not(bits)) /= '11111111') error stop 'complement and xor'
      do amount = 1, 7
         write(expected, '(b8.8)') iand(ishft(i, amount), 255)
         if (shift_l(bits, amount) /= expected) error stop 'left shift'
         write(expected, '(b8.8)') ishft(i, -amount)
         if (shift_r(bits, amount) /= expected) error stop 'right shift'
      end do
   end do
   print '(a)', '11111111 + 00000001 = '//add('11111111', '00000001')
   print '(a)', '00000000 - 00000001 = '//sub('00000000', '00000001')
   print '(a)', 'Left shift 00010101 by 2: '//shift_l('00010101', 2)
   print '(a)', 'All 256 eight-bit values passed arithmetic, logical and shift checks.'
   print '(a)', 'PASS bstrith'
end program demo_binary_strings
