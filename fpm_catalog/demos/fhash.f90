program main
   use fhash, only: fhash_tbl_t, key => fhash_key
   implicit none
   type(fhash_tbl_t) :: table
   integer :: count
   call table%set(key('samples'), value=128)
   call table%set(key('samples'), value=256)
   call table%get(key('samples'), count)
   if (count /= 256) error stop 'incorrect table lookup'
   print *, 'Updated sample count:', count
   print *, 'PASS fhash'
end program
