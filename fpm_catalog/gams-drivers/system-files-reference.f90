! Independent MIT consumer; see licenses/workflows-ten-drivers-MIT.txt.
program main
   use M_system, only: system_mkdir,system_isdir,system_isreg,system_remove,system_rmdir,R_USR,W_USR,X_USR
   implicit none
   integer :: status,unit,n,j
   character(64) :: content,loaded
   logical :: exists
   status=system_mkdir('system-fixture',iany([R_USR,W_USR,X_USR]))
   if(status/=0.or..not.system_isdir('system-fixture')) error stop 'Directory creation'
   if(system_isreg('system-fixture')) error stop 'Directory misclassified'
   do n=0,64
      do j=1,n
         content(j:j)=achar(mod(17*j+n,128))
      end do
      open(newunit=unit,file='system-fixture/data.bin',status='new',access='stream',form='unformatted')
      write(unit) content(:n)
      close(unit)
      if(.not.system_isreg('system-fixture/data.bin')) error stop 'Regular-file type'
      if(system_isdir('system-fixture/data.bin')) error stop 'File misclassified'
      open(newunit=unit,file='system-fixture/data.bin',status='old',access='stream',form='unformatted')
      if(n>0) read(unit) loaded(:n)
      close(unit)
      if(n>0) then
         if(loaded(:n)/=content(:n)) error stop 'Binary payload'
      end if
      status=system_remove('system-fixture/data.bin')
      if(status/=0) error stop 'Remove file'
      inquire(file='system-fixture/data.bin',exist=exists)
      if(exists) error stop 'File remains'
   end do
   status=system_rmdir('system-fixture')
   if(status/=0.or.system_isdir('system-fixture')) error stop 'Remove directory'
   print '(a)', '65 Linux binary file lifecycles, lengths 0..64; directory/file type checks'
   print '(a)', 'PASS system-files-reference'
end program
