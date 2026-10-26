program main
   use M_attr, only: attr, attr_mode
   implicit none
   character(:), allocatable :: text
   ! Plain output works in the browser's output pane too.
   call attr_mode(manner='plain')
   text = attr('<bold>Fortran<reset>')
   if (text /= 'Fortran') error stop 'incorrect plain-text conversion'
   print *, text
   print *, 'PASS m_attr'
end program main
