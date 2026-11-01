! Independent MIT consumer; see licenses/interop-ten-drivers-MIT.txt.
program main
   use os, only: mkdir,rmdir,rename,unlink
   use os_path, only: join,exists,isdir,isfile,getsize,basename,dirname,normpath
   implicit none
   character(:),allocatable :: folder,path,moved
   character(32) :: payload,readback
   integer :: status,n,unit
   call mkdir('os-fixture',stat=status)
   if(status/=0 .or. .not.isdir('os-fixture')) error stop 'mkdir root'
   folder=join('os-fixture','nested')
   call mkdir(folder,stat=status)
   if(status/=0 .or. .not.isdir(folder)) error stop 'mkdir nested'
   if(normpath('os-fixture/./nested/../nested')/=folder) error stop 'Relative normalization'
   if(normpath('/alpha/./beta/../gamma')/='/alpha/gamma') error stop 'Absolute normalization'
   path=join(folder,'input.bin')
   moved=join(folder,'output.bin')
   if(basename(path)/='input.bin' .or. dirname(path)/=folder) error stop 'Path parts'
   do n=0,32
      payload=repeat(achar(65+mod(n,26)),32)
      open(newunit=unit,file=path,status='new',access='stream',form='unformatted')
      write(unit) payload(:n)
      close(unit)
      if(.not.isfile(path) .or. getsize(path)/=n) error stop 'File size'
      call rename(path,moved,stat=status)
      if(status/=0 .or. exists(path) .or. .not.isfile(moved)) error stop 'Rename'
      if(getsize(moved)/=n) error stop 'Renamed size'
      open(newunit=unit,file=moved,status='old',access='stream',form='unformatted')
      if(n>0) read(unit) readback(:n)
      close(unit)
      if(n>0) then
         if(readback(:n)/=payload(:n)) error stop 'Renamed content'
      end if
      call unlink(moved,stat=status)
      if(status/=0 .or. exists(moved)) error stop 'Unlink'
   end do
   call rmdir(folder,stat=status)
   if(status/=0 .or. exists(folder)) error stop 'rmdir nested'
   call rmdir('os-fixture',stat=status)
   if(status/=0 .or. exists('os-fixture')) error stop 'rmdir root'
   print '(a)', '33 Linux file lifecycle traces and exact path normalization/parts'
   print '(a)', 'PASS os-path-reference'
end program
