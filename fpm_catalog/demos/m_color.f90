program main
   use M_color, only: color_name2rgb
   implicit none
   real :: red, green, blue
   call color_name2rgb('red', red, green, blue)
   if (abs(red-100.0) > 1.e-5 .or. abs(green)+abs(blue) > 1.e-5) error stop 'incorrect red'
   print *, 'Red as RGB percentages:', red, green, blue
   print *, 'PASS m_color'
end program
