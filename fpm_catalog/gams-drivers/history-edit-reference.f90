! Independent MIT consumer; see licenses/workflows-ten-drivers-MIT.txt.
program main
   use M_history, only: redo
   implicit none
   character(1024) :: line
   character(40) :: original(12),edited(12)
   character(20) :: number
   character(80) :: change
   integer :: i,script
   do i=1,12
      write(original(i),'(a,i2.2,a,i0)') 'parameter_',i,' = ',1000+i
      write(edited(i),'(a,i2.2,a,i0)') 'parameter_',i,' = ',2000+i
      line=original(i)
      call redo(line)
      if(line/=original(i)) error stop 'Initial history recording'
   end do
   do i=1,12
      open(newunit=script,status='scratch',form='formatted',action='readwrite')
      write(change,'(a,i0,a,i0,a)') 'c/',1000+i,'/',2000+i,'/'
      write(script,'(a)') trim(change),''
      rewind(script)
      write(number,'(i0)') i
      line='r '//trim(number)
      call redo(line,lun=script)
      close(script)
      if(line/=edited(i)) error stop 'Recall substitution'
      open(newunit=script,status='scratch',form='formatted',action='readwrite')
      write(script,'(a)') ''
      rewind(script)
      line='r '//trim(number)
      call redo(line,lun=script)
      close(script)
      if(line/=original(i)) error stop 'Original history mutated'
   end do
   print '(a)', '12 recorded commands; exact edited recalls and unchanged originals using 1024-character buffers'
   print '(a)', 'PASS history-edit-reference'
end program
