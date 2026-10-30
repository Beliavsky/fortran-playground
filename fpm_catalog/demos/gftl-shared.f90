program main
   use, intrinsic :: iso_fortran_env, only: int32, real64
   use gFTL1_Integer32Vector
   use gFTL1_Integer32Real64Map
   implicit none
   type(Integer32Vector) :: vector
   type(Integer32Real64Map) :: squares
   integer(int32) :: i
   real(real64) :: value, total
   vector = Integer32Vector()
   squares = Integer32Real64Map()
   do i = 1, 8
      call vector%push_back(i)
      call squares%insert(i, real(i*i, real64))
   end do
   if (vector%size() /= 8 .or. squares%size() /= 8) error stop 'Container size mismatch'
   total = 0.0_real64
   do i = 1, 8
      if (vector%at(i) /= i) error stop 'Vector retrieval failed'
      value = squares%at(i)
      if (value /= real(i*i,real64)) error stop 'Map retrieval failed'
      total = total + value
      print '(i3,f10.1)', i, value
   end do
   if (total /= 204.0_real64) error stop 'Map value sum mismatch'
   print '(a,f8.1)', 'Sum of stored squares: ', total
   print '(a)', 'PASS gftl-shared'
end program main
