! Use a file-output device; this example needs no display or font files.
program main
   use M_draw, only: voutput, vinit, prefsize, ortho2, color, clear, move2, draw2, vexit, D_BLACK, D_BLUE
   implicit none
   integer :: i, unit, status, bytes, width, height, maximum, red, green, blue, blue_pixels
   real :: x, y
   character(len=2048) :: line
   call voutput('drawing.ppm')
   call prefsize(400, 300)
   call vinit('ppm')
   call ortho2(0.0, 1.0, 0.0, 1.0)
   call color(D_BLACK)
   call clear()
   call color(D_BLUE)
   call move2(0.0, 0.0)
   do i = 1, 20
      x = real(i)/20.0
      y = x*x
      call draw2(x, y)
   end do
   call vexit()
   inquire(file='drawing.ppm', size=bytes, iostat=status)
   if (status /= 0 .or. bytes < 100) error stop 'PPM file missing or empty'
   open(newunit=unit, file='drawing.ppm', status='old', action='read', iostat=status)
   if (status /= 0) error stop 'PPM read failed'
   read(unit, '(a)') line
   if (trim(line) /= 'P3') error stop 'PPM format mismatch'
   call next_header_line()
   read(line, *) width, height
   if (width /= 400 .or. height /= 300) error stop 'PPM dimensions mismatch'
   call next_header_line()
   read(line, *) maximum
   if (maximum /= 255) error stop 'PPM color range mismatch'
   blue_pixels = 0
   do i = 1, width*height
      read(unit, *, iostat=status) red, green, blue
      if (status /= 0) error stop 'PPM pixel read failed'
      if (min(red,green,blue) < 0 .or. max(red,green,blue) > maximum) error stop 'PPM pixel range failed'
      if (blue > red .and. blue > green) blue_pixels = blue_pixels + 1
   end do
   close(unit)
   if (blue_pixels < 20) error stop 'Curve pixels missing'
   print '(a,i0,a,i0)', 'Generated drawing.ppm, bytes: ', bytes, ', blue pixels: ', blue_pixels
   print '(a)', 'Twenty-segment curve: y = x*x, 0 <= x <= 1'
   print '(a)', 'PASS m_draw'
contains
   subroutine next_header_line()
      do
         read(unit, '(a)', iostat=status) line
         if (status /= 0) error stop 'PPM header read failed'
         if (len_trim(line) == 0) cycle
         if (line(1:1) /= '#') exit
      end do
   end subroutine next_header_line
end program main
