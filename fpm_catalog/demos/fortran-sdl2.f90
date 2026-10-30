! Headless software surfaces: no window, display server or event loop.
program headless_sdl
   use, intrinsic :: iso_c_binding, only: c_f_pointer, c_int32_t, c_int64_t, c_int, c_char, c_null_char
   use sdl2, only: sdl_surface, sdl_pixel_format, sdl_rect, sdl_init, sdl_quit, &
      sdl_create_rgb_surface, sdl_fill_rect, sdl_map_rgb, sdl_free_surface
   use sdl2_image, only: img_init, IMG_INIT_PNG, img_load, img_quit
   implicit none
   type(sdl_surface), pointer :: surface, loaded
   type(sdl_pixel_format), pointer :: format
   type(sdl_rect) :: rectangle
   integer(c_int32_t), pointer :: pixels(:)
   integer(c_int32_t) :: colors(3)
   integer :: status, i, unit, bytes
   logical :: exists
   character(len=8) :: signature
   character(len=*), parameter :: filename = 'fortran-sdl2-bars.png'

   ! The pinned Fortran bindings provide IMG_Load but omit IMG_SavePNG.
   ! This standard C interface supplies only the missing PNG-save declaration.
   interface
      function save_png(image, name) bind(c, name='IMG_SavePNG') result(rc)
         import :: sdl_surface, c_char, c_int
         type(sdl_surface), intent(in) :: image
         character(kind=c_char), intent(in) :: name(*)
         integer(c_int) :: rc
      end function save_png
   end interface

   if (sdl_init(0) /= 0) error stop 'SDL initialization'
   if (iand(img_init(IMG_INIT_PNG), IMG_INIT_PNG) == 0) error stop 'PNG initialization'
   surface => sdl_create_rgb_surface(0, 640, 360, 32, &
      int(z'00FF0000',c_int64_t), int(z'0000FF00',c_int64_t), &
      int(z'000000FF',c_int64_t), 0_c_int64_t)
   if (.not. associated(surface)) error stop 'surface allocation'
   call c_f_pointer(surface%format, format)
   rectangle = sdl_rect(0, 0, surface%w, surface%h)
   status = sdl_fill_rect(surface, rectangle, sdl_map_rgb(format, 245, 245, 245))
   if (status /= 0) error stop 'background fill'
   colors = [sdl_map_rgb(format, 35, 95, 195), sdl_map_rgb(format, 210, 65, 50), &
             sdl_map_rgb(format, 35, 155, 100)]
   do i = 1, 3
      rectangle = sdl_rect(40+200*(i-1), 40+70*(i-1), 160, 280-70*(i-1))
      status = sdl_fill_rect(surface, rectangle, colors(i))
      if (status /= 0) error stop 'rectangle fill'
   end do
   call c_f_pointer(surface%pixels, pixels, [surface%pitch*surface%h/4])
   if (pixels(1) /= sdl_map_rgb(format, 245, 245, 245)) error stop 'background pixel'
   do i = 1, 3
      if (pixels(300*(surface%pitch/4)+120+200*(i-1)+1) /= colors(i)) &
         error stop 'bar color'
   end do
   nullify(pixels, format)
   status = save_png(surface, filename//c_null_char)
   if (status /= 0) error stop 'PNG save'
   call sdl_free_surface(surface)
   nullify(surface)

   ! Load the PNG through the package API and check its dimensions.
   loaded => img_load(filename//c_null_char)
   if (.not. associated(loaded)) error stop 'PNG reload'
   if (loaded%w /= 640 .or. loaded%h /= 360) error stop 'image dimensions'
   print '(a,i0,a,i0)', 'Reloaded PNG: ', loaded%w, ' x ', loaded%h
   call sdl_free_surface(loaded)
   nullify(loaded)
   call img_quit()
   call sdl_quit()

   inquire(file=filename, exist=exists, size=bytes)
   if (.not. exists .or. bytes < 500) error stop 'PNG missing or too small'
   open(newunit=unit, file=filename, access='stream', form='unformatted', status='old')
   read(unit) signature
   close(unit)
   if (signature /= achar(137)//'PNG'//achar(13)//achar(10)//achar(26)//achar(10)) &
      error stop 'PNG signature'
   print '(a,i0)', 'PNG bytes: ', bytes
   print '(a)', 'PASS fortran-sdl2'
end program headless_sdl
