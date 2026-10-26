program main
   use M_sets, only: union, intersect
   implicit none
   integer, allocatable :: combined(:), common(:)
   combined = union([1,3,5], [2,3,4])
   common = intersect([1,3,5], [2,3,4])
   if (any(combined /= [1,2,3,4,5])) error stop 'incorrect union'
   if (size(common) /= 1) error stop 'incorrect intersection size'
   if (common(1) /= 3) error stop 'incorrect intersection'
   print *, 'Union:', combined
   print *, 'Intersection:', common
   print *, 'PASS m_sets'
end program main
