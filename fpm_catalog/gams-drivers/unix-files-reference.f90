! Independent MIT consumer; see licenses/interop-ten-drivers-MIT.txt.
program main
   use unix
   implicit none
   type(c_stat_t) :: info
   character(128) :: content,readback
   integer :: n,j,unit,status,bytes
   logical :: exists
   do n=0,128
      do j=1,n
         content(j:j)=achar(mod(31*j+n,128))
      end do
      open(newunit=unit,file='posix-fixture.bin',status='new',access='stream',form='unformatted')
      write(unit) content(:n)
      close(unit)
      status=c_stat('posix-fixture.bin'//c_null_char,info)
      if(status/=0) error stop 'stat existing'
      inquire(file='posix-fixture.bin',size=bytes)
      if(info%st_size/=n .or. bytes/=n) error stop 'Byte size'
      open(newunit=unit,file='posix-fixture.bin',status='old',access='stream',form='unformatted')
      if(n>0) read(unit) readback(:n)
      close(unit)
      if(n>0) then
         if(readback(:n)/=content(:n)) error stop 'Content'
      end if
      status=c_unlink('posix-fixture.bin'//c_null_char)
      if(status/=0) error stop 'unlink'
      inquire(file='posix-fixture.bin',exist=exists)
      if(exists) error stop 'Unlink left file'
      status=c_stat('posix-fixture.bin'//c_null_char,info)
      if(status==0) error stop 'stat absent'
   end do
   print '(a)', '129 Linux POSIX file lifecycles, lengths 0..128 including arbitrary bytes'
   print '(a)', 'PASS unix-files-reference'
end program
