! Example: Coarrays: identify images
! Coarray images: 2
! Load this example in Advanced mode with a verified coarray image count.
program coarray_images
   use iso_fortran_env, only: output_unit
   implicit none
   integer :: turn

   ! Synchronize and flush so the output appears in image order.
   do turn = 1, num_images()
      if (this_image() == turn) then
         print '(A,I0,A,I0)', 'Image ', this_image(), ' of ', num_images()
         flush(output_unit)
      end if
      sync all
   end do
end program coarray_images
