program huffman_round_trip
   use huffman_mod, only: hftree
   implicit none
   character(*), parameter :: text = repeat('Fortran compresses repeated text. ',100)
   character(len(text)) :: restored
   integer :: unit, original_size, compressed_size, restored_size
   open(newunit=unit,file='message.txt',status='replace',access='stream',form='unformatted')
   write(unit) text
   close(unit)
   block
      type(hftree) :: encoder
      call encoder%encode('message.txt')
   end block
   block
      type(hftree) :: decoder
      call decoder%decode('message.txt.bin')
   end block
   inquire(file='message.txt',size=original_size)
   inquire(file='message.txt.bin',size=compressed_size)
   inquire(file='message.txt.bin.txt',size=restored_size)
   if (restored_size/=len(text)) error stop 'Length mismatch'
   open(newunit=unit,file='message.txt.bin.txt',access='stream',form='unformatted',status='old')
   read(unit) restored
   close(unit)
   if (restored/=text) error stop 'Round-trip mismatch'
   print '(a,i0)', 'Original bytes: ', original_size
   print '(a,i0)', 'Compressed bytes (including tree): ', compressed_size
   print '(a)', 'Decoded text matches every original byte.'
   print *, 'PASS fortran_huffman'
end program
