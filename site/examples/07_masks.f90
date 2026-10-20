! Example: Arrays: masks and selection
! Adapted from https://github.com/Beliavsky/FortranTip/blob/main/count_pack.f90
! Try changing the selection from v > 0 to v < 0.
program masked_arrays
   implicit none
   integer :: v(3) = [1,-4,9], clipped(3)
   print '(a,*(i0,1x))', 'Positive values: ', pack(v,v>0)
   print '(a,i0)', 'Positive count: ', count(v>0)
   print '(a,i0)', 'Positive sum: ', sum(v,mask=v>0)
   print '(a,2(l1,1x))', 'Any positive, all positive: ', any(v>0), all(v>0)
   clipped = v
   where (clipped < 0) clipped = 0
   print '(a,*(i0,1x))', 'Negative values replaced by zero: ', clipped
end program masked_arrays
