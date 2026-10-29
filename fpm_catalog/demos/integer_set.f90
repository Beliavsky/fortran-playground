program main
   use iso_c_binding, only: c_int32_t, c_int64_t
   use integer32_set, only: int32_set, new_int32_set
   use integer64_set, only: int64_set, new_int64_set
   implicit none
   type(int32_set) :: small
   type(int64_set) :: large
   integer :: i
   small = new_int32_set()
   do i = 5, 1, -1
      call small%push(int(i, c_int32_t))
   end do
   call small%push(3_c_int32_t)
   if (small%size /= 5) error stop 'duplicate insertion'
   call small%pop(2_c_int32_t)
   call small%sort()
   if (small%size /= 4) error stop 'removal count'
   if (any(small%data /= [1, 3, 4, 5])) error stop 'sorted contents'
   print *, 'Unique sorted values after removing 2:', small%data
   large = new_int64_set()
   call large%push(5000000000_c_int64_t)
   call large%push(5000000000_c_int64_t)
   if (large%size /= 1) error stop '64-bit duplicate'
   if (large%data(1) /= 5000000000_c_int64_t) error stop '64-bit value'
   print *, '64-bit value:', large%data
   call small%destroy()
   call large%destroy()
   print *, 'PASS integer_set'
end program
