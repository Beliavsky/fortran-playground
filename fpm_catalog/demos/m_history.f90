! M_history's redo editor, scripted through its optional input unit.
! No shell commands are executed. The history and editing script are scratch files.
program main
   use M_history, only: redo
   implicit none
   ! Use the author's 1024-character example buffer (short buffers are unsupported here).
   character(len=1024) :: line
   integer :: script
   line='temperature = 290'
   call redo(line)
   if (trim(line)/='temperature = 290') error stop 'History changed initial text'
   line='pressure = 1000'
   call redo(line)
   open(newunit=script,status='scratch',action='readwrite',form='formatted')
   write(script,'(a)') 'c/290/300/', ''
   rewind(script)
   line='r 1'
   call redo(line,lun=script)
   if (trim(line)/='temperature = 300') error stop 'Recall/substitution check'
   print '(a)', 'Recalled and edited: '//trim(line)
   close(script)
   open(newunit=script,status='scratch',action='readwrite',form='formatted')
   write(script,'(a)') ''
   rewind(script)
   line='r 2'
   call redo(line,lun=script)
   if (trim(line)/='pressure = 1000') error stop 'Original history was modified'
   print '(a)', 'Original history retained: '//trim(line)
   close(script)
   print '(a)', 'PASS m_history'
end program main
