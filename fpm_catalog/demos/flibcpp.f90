! Sorting and searching through the upstream C++ standard-library wrappers.
program main
   use, intrinsic :: iso_c_binding, only: c_int32_t
   use flc_algorithm, only: sort, binary_search
   implicit none
   integer(c_int32_t) :: values(7) = [9, -5, 2, 1, 4, 1, -2]
   integer(c_int32_t), parameter :: expected(7) = [-5, -2, 1, 1, 2, 4, 9]
   call sort(values)
   if (any(values /= expected)) error stop 'Sorting result is incorrect'
   if (binary_search(values, 2_c_int32_t) /= 5) error stop 'Existing key was not found'
   if (binary_search(values, 3_c_int32_t) /= 0) error stop 'Absent key was reported present'
   print '(a,7(i0,1x))', 'Sorted values: ', values
   print '(a)', 'Search: 2 is at position 5; 3 is absent'
   print '(a)', 'PASS flibcpp'
end program main
