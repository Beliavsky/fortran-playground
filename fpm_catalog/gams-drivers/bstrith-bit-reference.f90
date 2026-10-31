! Original GAMS N2 API driver. MIT: licenses/arithmetic-drivers-MIT.txt.
program main
   use bstrith, only: shift_l, shift_r, xor, not, add, sub
   implicit none
   integer :: value, amount, left, right, checks
   character(8) :: bits, mask, expected
   character(4) :: a, b, reference
   checks = 0
   do value = 0, 255
      write(bits,'(b8.8)') value
      do amount = 1, 7
         write(expected,'(b8.8)') iand(ishft(value,amount),255)
         if (shift_l(bits,amount) /= expected) error stop 'left shift'
         write(expected,'(b8.8)') ishft(value,-amount)
         if (shift_r(bits,amount) /= expected) error stop 'right shift'
         checks = checks + 2
      end do
      write(expected,'(b8.8)') ieor(value,255)
      if (not(bits) /= expected) error stop 'bit complement'
      mask = '10100101'
      write(expected,'(b8.8)') ieor(value,165)
      if (xor(bits,mask) /= expected) error stop 'bit xor'
      write(expected,'(b8.8)') modulo(value+1,256)
      if (add(bits,'00000001') /= expected) error stop '8-bit modular addition'
      write(expected,'(b8.8)') modulo(value-1,256)
      if (sub(bits,'00000001') /= expected) error stop '8-bit modular subtraction'
      checks = checks + 4
   end do
   do left = 0, 15
      do right = 0, 15
         write(a,'(b4.4)') left
         write(b,'(b4.4)') right
         write(reference,'(b4.4)') modulo(left+right,16)
         if (add(a,b) /= reference) error stop '4-bit modular addition'
         write(reference,'(b4.4)') modulo(left-right,16)
         if (sub(a,b) /= reference) error stop '4-bit modular subtraction'
         checks = checks + 2
      end do
   end do
   if (checks /= 5120) error stop 'case count'
   print '(a)', '10100101 shifted left by 2: '//shift_l('10100101',2)
   print '(a)', '10100101 XOR 11110000: '//xor('10100101','11110000')
   print '(a,i0)', 'Independent bit/arithmetic checks passed: ', checks
   print '(a)', 'Shift distances 1..7 for every 8-bit value; all pairs of 4-bit arithmetic operands.'
   print '(a)', 'Out-of-range shifts, malformed strings and wider strings are outside this example.'
   print '(a)', 'PASS bstrith-bit-reference'
end program
