program main
   use forimage, only: format_pnm,ik
   implicit none
   integer, parameter :: width=128,height=96
   type(format_pnm) :: image,negative,restored
   integer(ik) :: pixels(height,3*width)
   integer :: i,j
   do i=1,height
      do j=1,width
         pixels(i,3*j-2)=int(255*(j-1)/(width-1),ik)
         pixels(i,3*j-1)=int(255*(i-1)/(height-1),ik)
         pixels(i,3*j)=int(255-255*(j-1)/(width-1),ik)
      end do
   end do
   call image%set_pnm(encoding='binary',file_format='ppm',width=width,height=height, &
      max_color=255,comment='Generated color gradient',pixels=pixels)
   call image%export_pnm('01_gradient')
   negative=image
   call negative%negative()
   if (any(negative%pixels/=255_ik-pixels)) error stop 'Color inversion failed'
   call negative%export_pnm('02_negative')
   call restored%import_pnm('01_gradient','ppm','binary')
   if (any(restored%pixels/=pixels)) error stop 'Image round trip failed'
   print *, 'Original color gradient and its negative are displayed below.'
   print *, 'PASS forimage'
end program
