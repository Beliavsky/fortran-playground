! Example: Coarrays: exchange values around a ring
! Coarray images: 2
! Each image reads the value stored on its next neighbor.
program coarray_exchange
   use iso_fortran_env, only: output_unit
   implicit none
   integer :: value[*], received, neighbor, turn

   value = 100 * this_image()
   sync all ! Every image must initialize its value before anyone reads it.
   neighbor = mod(this_image(), num_images()) + 1
   received = value[neighbor]
   sync all

   do turn = 1, num_images()
      if (this_image() == turn) then
         print '(A,I0,A,I0)', 'Image ', this_image(), ' received ', received
         flush(output_unit)
      end if
      sync all
   end do
end program coarray_exchange
