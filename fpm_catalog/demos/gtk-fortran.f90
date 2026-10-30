! Cairo drawing adapted from gtk-fortran examples/cairo-basics.f90.
! Copyright (C) 2011 The gtk-fortran team (Jerry DeLisle and Vincent Magnin).
! GPL-3.0-or-later WITH GCC-exception-3.1; see the upstream LICENSE files.
program headless_cairo
   use, intrinsic :: iso_c_binding, only: c_ptr, c_associated, c_int, c_double, c_null_char
   use gtk, only: CAIRO_FORMAT_ARGB32, CAIRO_FONT_SLANT_NORMAL, CAIRO_FONT_WEIGHT_NORMAL
   use cairo, only: cairo_image_surface_create, cairo_create, cairo_surface_status, &
      cairo_status, cairo_set_source_rgb, cairo_paint, cairo_set_line_width, &
      cairo_move_to, cairo_curve_to, cairo_stroke, cairo_arc, cairo_select_font_face, &
      cairo_set_font_size, cairo_show_text, cairo_surface_write_to_png, &
      cairo_destroy, cairo_surface_destroy
   implicit none
   type(c_ptr) :: surface, cr
   integer(c_int) :: status
   integer :: i, unit, bytes
   logical :: exists
   character(len=8) :: signature
   real(c_double), parameter :: pi = acos(-1.0_c_double)
   character(len=*), parameter :: filename = 'gtk-fortran-cairo.png'

   ! An image surface requires neither gtk_init() nor a display server.
   surface = cairo_image_surface_create(CAIRO_FORMAT_ARGB32, 640_c_int, 400_c_int)
   if (.not. c_associated(surface)) error stop 'null surface'
   if (cairo_surface_status(surface) /= 0) error stop 'image surface creation'
   cr = cairo_create(surface)
   if (.not. c_associated(cr)) error stop 'null drawing context'
   if (cairo_status(cr) /= 0) error stop 'drawing context creation'
   call cairo_set_source_rgb(cr, 1.0_c_double, 1.0_c_double, 1.0_c_double)
   call cairo_paint(cr)

   call cairo_set_source_rgb(cr, 0.12_c_double, 0.28_c_double, 0.65_c_double)
   call cairo_set_line_width(cr, 4.0_c_double)
   call cairo_move_to(cr, 40.0_c_double, 310.0_c_double)
   call cairo_curve_to(cr, 160.0_c_double, 20.0_c_double, 430.0_c_double, &
      490.0_c_double, 600.0_c_double, 110.0_c_double)
   call cairo_stroke(cr)

   do i = 0, 4
      call cairo_set_source_rgb(cr, 0.85_c_double, 0.15_c_double+i*0.10_c_double, 0.12_c_double)
      call cairo_arc(cr, 130.0_c_double+95.0_c_double*i, 220.0_c_double, &
         24.0_c_double+3.0_c_double*i, 0.0_c_double, 2*pi)
      call cairo_stroke(cr)
   end do

   call cairo_set_source_rgb(cr, 0.12_c_double, 0.12_c_double, 0.12_c_double)
   call cairo_select_font_face(cr, 'Sans'//c_null_char, &
      CAIRO_FONT_SLANT_NORMAL, CAIRO_FONT_WEIGHT_NORMAL)
   call cairo_set_font_size(cr, 28.0_c_double)
   call cairo_move_to(cr, 40.0_c_double, 55.0_c_double)
   call cairo_show_text(cr, 'gtk-fortran: Cairo without a window'//c_null_char)
   if (cairo_status(cr) /= 0) error stop 'drawing failed'
   status = cairo_surface_write_to_png(surface, filename//c_null_char)
   call cairo_destroy(cr)
   call cairo_surface_destroy(surface)
   if (status /= 0) error stop 'PNG write failed'
   inquire(file=filename, exist=exists, size=bytes)
   if (.not. exists .or. bytes < 1000) error stop 'PNG missing or too small'
   open(newunit=unit, file=filename, access='stream', form='unformatted', status='old')
   read(unit) signature
   close(unit)
   if (signature /= achar(137)//'PNG'//achar(13)//achar(10)//achar(26)//achar(10)) &
      error stop 'PNG signature'
   print '(a,i0)', 'PNG bytes: ', bytes
   print '(a)', 'PASS gtk-fortran'
end program headless_cairo
