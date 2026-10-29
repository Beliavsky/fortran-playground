program morton_neighbor
   use orbs
   implicit none
   type(operable_bitset) :: key, neighbor, one, mask_x, mask_y, expected
   character(4) :: text, expected_text
   integer :: code, x, y, next_x, next_code
   mask_x = operable_bitset('1010')
   mask_y = operable_bitset('0101')
   ! A 4-bit Morton key interleaves two bits of x with two bits of y.
   do code=0,15
      write(text,'(b4.4)') code
      key = operable_bitset(text)
      one = orbs_one(mold=key)
      neighbor = (((key.or.mask_y)+one).and.mask_x).or.(key.and.mask_y)
      ! Independent reference using ordinary integer bit operations.
      x = ibits(code,1,1) + 2*ibits(code,3,1)
      y = ibits(code,0,1) + 2*ibits(code,2,1)
      next_x = modulo(x+1,4)
      next_code = 2*ibits(next_x,0,1) + 8*ibits(next_x,1,1) &
         + ibits(y,0,1) + 4*ibits(y,1,1)
      write(expected_text,'(b4.4)') next_code
      expected = operable_bitset(expected_text)
      if (neighbor/=expected) error stop 'Morton neighbor mismatch'
      if (code==3) print '(a)', 'Morton key '//text//' -> x neighbor '//expected_text
   end do
   print '(a)', 'Verified all 16 cells, including periodic wraparound.'
   print *, 'PASS orbs'
end program morton_neighbor
