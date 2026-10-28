program main
   use filesystem, only: normal,mkdir,is_dir,is_file,copy_file,file_size,remove
   implicit none
   integer :: unit
   logical :: ok
   character(40) :: text
   print '(a,a)', 'Normalized path: ',normal('./demo_files//part/../source.txt')
   call mkdir('demo_files')
   if (.not.is_dir('demo_files')) error stop 'Directory creation failed'
   open(newunit=unit,file='demo_files/source.txt',status='replace')
   write(unit,'(a)') 'Hello from the temporary sandbox'
   close(unit)
   call copy_file('demo_files/source.txt','demo_files/copy.txt',ok=ok)
   if (.not.ok.or..not.is_file('demo_files/copy.txt')) error stop 'Copy failed'
   if (file_size('demo_files/source.txt')/=file_size('demo_files/copy.txt')) error stop
   open(newunit=unit,file='demo_files/copy.txt',status='old')
   read(unit,'(a)') text
   close(unit)
   if (trim(text)/='Hello from the temporary sandbox') error stop 'Contents differ'
   print '(a,i0)', 'Copied file size in bytes: ',file_size('demo_files/copy.txt')
   print '(a,a)', 'Read back: ',trim(text)
   call remove('demo_files/copy.txt')
   call remove('demo_files/source.txt')
   call remove('demo_files')
   if (is_dir('demo_files')) error stop 'Cleanup failed'
   print *, 'PASS ffilesystem'
end program
