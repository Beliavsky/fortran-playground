program main
   use forcolormap, only: Colormap, wp
   implicit none
   type(Colormap) :: colors
   integer :: red, green, blue, i
   call colors%set('viridis', 0.0_wp, 1.0_wp)
   do i = 0, 4
      call colors%compute_RGB(real(i,wp)/4, red, green, blue)
      if (min(red,green,blue) < 0 .or. max(red,green,blue) > 255) error stop 'RGB out of range'
      print *, 'Value and RGB:', real(i,wp)/4, red, green, blue
      if (i == 0 .and. (red /= 68 .or. green /= 1 .or. blue /= 84)) error stop 'incorrect viridis endpoint'
   end do
   print *, 'PASS forcolormap'
end program
