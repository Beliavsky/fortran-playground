! Independent API consumer; MIT: licenses/raster-distributions-drivers-MIT.txt.
program raster_reference
   use, intrinsic :: iso_c_binding, only: c_int,c_int32_t,c_int64_t,c_char,c_null_char,c_f_pointer
   use, intrinsic :: iso_fortran_env, only: int8
   use sdl2, only: sdl_surface,sdl_pixel_format,sdl_rect,sdl_init,sdl_quit,sdl_create_rgb_surface, &
      sdl_fill_rect,sdl_map_rgb,sdl_convert_surface,sdl_free_surface
   use sdl2_image, only: img_init,IMG_INIT_PNG,img_load,img_quit
   implicit none
   integer, parameter :: width=85,height=65
   integer, parameter :: boxes(4,4) = reshape([10,15,45,30,35,25,40,35,-15,-10,35,30,70,50,40,35],[4,4])
   integer, parameter :: rgb(3,5) = reshape([12,34,56,240,20,60,30,200,80,40,70,230,250,220,15],[3,5])
   type(sdl_surface), pointer :: surface,loaded,converted
   type(sdl_pixel_format), pointer :: format
   type(sdl_rect) :: rectangle
   integer(c_int32_t) :: expected(width,height)
   integer(int8) :: header(24)
   integer :: i,x,y,color,status,unit,checks
   interface
      ! The pinned bindings omit this standard SDL2_image save declaration.
      function save_png(image,name) bind(c,name='IMG_SavePNG') result(rc)
         import sdl_surface,c_char,c_int
         type(sdl_surface), intent(in) :: image
         character(c_char), intent(in) :: name(*)
         integer(c_int) :: rc
      end function save_png
   end interface
   if (sdl_init(0) /= 0) error stop 'SDL initialization'
   if (iand(img_init(IMG_INIT_PNG),IMG_INIT_PNG) == 0) error stop 'PNG initialization'
   surface => sdl_create_rgb_surface(0,width,height,32,int(z'00FF0000',c_int64_t), &
      int(z'0000FF00',c_int64_t),int(z'000000FF',c_int64_t),0_c_int64_t)
   if (.not. associated(surface)) error stop 'software surface creation'
   call c_f_pointer(surface%format,format)
   if (.not. associated(format)) error stop 'surface pixel format'
   rectangle = sdl_rect(0,0,width,height)
   status = sdl_fill_rect(surface,rectangle,sdl_map_rgb(format,rgb(1,1),rgb(2,1),rgb(3,1)))
   if (status /= 0) error stop 'background fill'
   do i = 1,4
      rectangle = sdl_rect(boxes(1,i),boxes(2,i),boxes(3,i),boxes(4,i))
      status = sdl_fill_rect(surface,rectangle,sdl_map_rgb(format,rgb(1,i+1),rgb(2,i+1),rgb(3,i+1)))
      if (status /= 0) error stop 'rectangle fill'
   end do
   do y = 0,height-1
      do x = 0,width-1
         color = 1
         do i = 1,4
            if (x >= boxes(1,i) .and. x < boxes(1,i)+boxes(3,i) &
               .and. y >= boxes(2,i) .and. y < boxes(2,i)+boxes(4,i)) color = i+1
         end do
         ! Native mask arithmetic supplies the expected pixel; no SDL mapping call.
         expected(x+1,y+1) = ior(ishft(int(rgb(1,color),c_int32_t),16), &
            ior(ishft(int(rgb(2,color),c_int32_t),8),int(rgb(3,color),c_int32_t)))
      end do
   end do
   checks = 0
   call check_pixels(surface)
   status = save_png(surface,'gams-sdl-raster.png'//c_null_char)
   if (status /= 0) error stop 'PNG export'
   open(newunit=unit,file='gams-sdl-raster.png',access='stream',form='unformatted',status='old',iostat=status)
   if (status /= 0) error stop 'native PNG open'
   read(unit,iostat=status) header
   close(unit)
   if (status /= 0) error stop 'native PNG header read'
   if (any(iand(int(header(:8)),255) /= [137,80,78,71,13,10,26,10])) error stop 'PNG signature'
   if (any(iand(int(header(13:16)),255) /= [73,72,68,82])) error stop 'PNG IHDR chunk'
   if (big_endian(header(17:20)) /= width .or. big_endian(header(21:24)) /= height) &
      error stop 'independent PNG dimensions'
   loaded => img_load('gams-sdl-raster.png'//c_null_char)
   if (.not. associated(loaded)) error stop 'PNG import'
   if (loaded%w /= width .or. loaded%h /= height) error stop 'imported PNG dimensions'
   converted => sdl_convert_surface(loaded,format,0)
   if (.not. associated(converted)) error stop 'standard pixel format conversion'
   call check_pixels(converted)
   call sdl_free_surface(converted)
   call sdl_free_surface(loaded)
   call sdl_free_surface(surface)
   nullify(converted,loaded,surface,format)
   call img_quit()
   call sdl_quit()
   if (checks /= 11050) error stop 'raster pixel count'
   print '(a)', '85x65 software surface: four overlapping/clipped rectangles and five known colors.'
   print '(a)', '11050 exact pixel references checked before and after PNG save/load.'
   print '(a)', 'Native PNG signature/dimensions checked; generated image is available for browser display.'
   print '(a)', 'PASS sdl-raster-reference'
contains
   subroutine check_pixels(image)
      type(sdl_surface), intent(in) :: image
      integer(c_int32_t), pointer :: pixels(:)
      integer :: ix,iy,index
      if (image%w /= width .or. image%h /= height .or. mod(image%pitch,4) /= 0) &
         error stop '32-bit image geometry'
      call c_f_pointer(image%pixels,pixels,[image%pitch*image%h/4])
      if (.not. associated(pixels)) error stop 'image pixels'
      do iy = 0,height-1
         do ix = 0,width-1
            index = iy*(image%pitch/4)+ix+1
            if (iand(pixels(index),int(z'00FFFFFF',c_int32_t)) /= expected(ix+1,iy+1)) &
               error stop 'independent raster reference'
            checks = checks+1
         end do
      end do
      nullify(pixels)
   end subroutine check_pixels
   integer function big_endian(bytes) result(value)
      integer(int8), intent(in) :: bytes(4)
      integer :: j
      value = 0
      do j = 1,4
         value = 256*value+iand(int(bytes(j)),255)
      end do
   end function big_endian
end program raster_reference
