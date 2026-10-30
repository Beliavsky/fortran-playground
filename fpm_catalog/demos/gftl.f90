! The catalog supplies this integer-vector instantiation of the gFTL templates.
program main
   use playground_gftl
   implicit none
   type(IntegerVector) :: values
   integer :: i, rc, total
   values = IntegerVector()
   do i = 1, 100
      call values%push_back(i*i, rc=rc)
      if (rc /= 0) error stop 'Vector insertion failed'
   end do
   if (values%size() /= 100) error stop 'Vector size mismatch'
   total = 0
   do i = 1, 100
      if (values%at(i) /= i*i) error stop 'Stored value mismatch'
      total = total + values%at(i)
   end do
   if (total /= 338350) error stop 'Sum of squares mismatch'
   print '(a,i0)', 'Vector size: ', values%size()
   print '(a,i0)', 'Sum of squares from 1 to 100: ', total
   print '(a)', 'PASS gftl'
end program main
