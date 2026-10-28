program cairo_spiral
   use iso_c_binding, only: c_ptr, c_associated, c_null_char, c_int
   use cairo
   use cairo_enums, only: CAIRO_FORMAT_ARGB32, CAIRO_STATUS_SUCCESS
   implicit none
   type(c_ptr) :: surface, context
   integer(c_int) :: status
   integer :: i
   real(8) :: theta, radius, pi
   surface = cairo_image_surface_create(CAIRO_FORMAT_ARGB32,400,400)
   if (.not. c_associated(surface)) error stop 'No surface'
   context = cairo_create(surface)
   if (.not. c_associated(context)) error stop 'No drawing context'
   call cairo_set_source_rgb(context,1.d0,1.d0,1.d0)
   call cairo_paint(context)
   pi = acos(-1.d0)
   call cairo_set_source_rgb(context,0.85d0,0.88d0,0.92d0)
   call cairo_set_line_width(context,1.d0)
   do i=1,3
      call cairo_arc(context,200.d0,200.d0,50.d0*i,0.d0,2*pi)
      call cairo_stroke(context)
   end do
   call cairo_set_source_rgb(context,0.10d0,0.30d0,0.75d0)
   call cairo_set_line_width(context,3.d0)
   call cairo_move_to(context,200.d0,200.d0)
   do i=1,720
      theta = 6*pi*i/720
      radius = 8*theta
      call cairo_line_to(context,200+radius*cos(theta),200+radius*sin(theta))
   end do
   call cairo_stroke(context)
   if (cairo_status(context)/=CAIRO_STATUS_SUCCESS) error stop 'Drawing failed'
   status = cairo_surface_write_to_png(surface,'spiral.png'//c_null_char)
   if (status/=CAIRO_STATUS_SUCCESS) error stop 'PNG write failed'
   if (cairo_image_surface_get_width(surface)/=400) error stop 'Width check'
   if (cairo_image_surface_get_height(surface)/=400) error stop 'Height check'
   call cairo_destroy(context)
   call cairo_surface_destroy(surface)
   print '(a)', 'Saved spiral.png: an Archimedean spiral r = 8*theta, 0 <= theta <= 6*pi.'
   print *, 'PASS cairo-fortran'
end program
