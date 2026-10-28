program png_round_trip
   use iso_c_binding, only: c_int, c_char, c_ptr, c_null_char, c_associated, c_f_pointer
   use stb_image_mod, only: c_stbi_load
   use stb_image_write_mod, only: write_image
   implicit none
   integer, parameter :: width=128, height=96
   integer :: pixels(width,height,3), i,j,k,index,status
   integer(c_int) :: nx,ny,channels
   type(c_ptr) :: image
   character(kind=c_char), pointer :: bytes(:)
   interface
      subroutine free_image(p) bind(c,name='stbi_image_free')
         import :: c_ptr
         type(c_ptr), value :: p
      end subroutine
   end interface
   do j=1,height
      do i=1,width
         pixels(i,j,:) = [255*(i-1)/(width-1),255*(j-1)/(height-1), &
            merge(220,40,mod((i-1)/16+(j-1)/16,2)==0)]
      end do
   end do
   status = write_image('gradient.png',pixels)
   if (status/=1) error stop 'PNG write failed'
   image = c_stbi_load('gradient.png'//c_null_char,nx,ny,channels,3_c_int)
   if (.not. c_associated(image)) error stop 'PNG read failed'
   if (nx/=width .or. ny/=height .or. channels/=3) error stop 'Image dimensions'
   call c_f_pointer(image,bytes,[width*height*3])
   index = 0
   do j=1,height
      do i=1,width
         do k=1,3
            index = index+1
            if (iachar(bytes(index))/=pixels(i,j,k)) error stop 'Pixel mismatch'
         end do
      end do
   end do
   call free_image(image)
   nullify(bytes)
   print '(a,i0,a,i0,a)', 'Verified every RGB pixel in ',width,' x ',height,' gradient.png'
   print *, 'PASS fortran_stb_image'
end program
