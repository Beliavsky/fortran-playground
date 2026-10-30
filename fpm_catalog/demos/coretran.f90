program main
   use iso_fortran_env, only: real64
   use m_sort, only: sort
   use m_KdTree, only: KdTree, KdTreeSearch
   implicit none
   integer :: a(6) = [7,-2,4,4,0,1], i, nearest, expected
   real(real64) :: x(20), y(20), distances(20)
   type(KdTree) :: tree
   type(KdTreeSearch) :: search
   call sort(a)
   if (any(a /= [-2,0,1,4,4,7])) error stop 'sorting'
   print '(a,6i4)', 'Sorted integers: ', a
   do i = 1, 20
      x(i) = real(mod(7*i,23),real64)/23
      y(i) = real(mod(11*i,29),real64)/29
   end do
   distances = (x-0.37_real64)**2+(y-0.62_real64)**2
   expected = minloc(distances,dim=1)
   tree = KdTree(x,y)
   nearest = search%nearest(tree,x,y,0.37_real64,0.62_real64)
   if (nearest /= expected) error stop 'nearest neighbor'
   print '(a,i0)', 'Nearest point index: ', nearest
   print '(a,f12.8)', 'Squared distance: ', distances(nearest)
   call tree%deallocate()
   print '(a)', 'PASS coretran'
end program main
