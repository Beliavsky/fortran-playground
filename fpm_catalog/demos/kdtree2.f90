program main
   use kdtree2_precision_module, only: kdkind
   use kdtree2_module, only: kdtree2, kdtree2_result, kdtree2_create, kdtree2_destroy, &
      kdtree2_n_nearest, kdtree2_r_nearest
   implicit none
   integer, parameter :: n = 30, neighbors = 4
   real(kdkind), target :: points(2,n), query(2)
   real(kdkind) :: direct(n), work(n), radius2
   type(kdtree2), pointer :: tree
   type(kdtree2_result) :: nearest(neighbors), within(n)
   integer :: i, j, index, expected(neighbors), found

   do i = 1, n
      points(:,i) = [real(mod(i*7,31),kdkind)/31, real(mod(i*11,37),kdkind)/37]
   end do
   query = [0.37_kdkind, 0.62_kdkind]
   do i = 1, n
      direct(i) = sum((points(:,i)-query)**2)
   end do
   work = direct
   do i = 1, neighbors
      expected(i) = minloc(work,dim=1)
      work(expected(i)) = huge(1.0_kdkind)
   end do
   tree => kdtree2_create(points, sort=.true., rearrange=.true.)
   call kdtree2_n_nearest(tree, query, neighbors, nearest)
   print '(a)', 'Nearest neighbors: index, squared distance'
   do i = 1, neighbors
      index = nearest(i)%idx
      if (index /= expected(i)) error stop 'nearest index'
      if (abs(nearest(i)%dis-direct(index)) > 1.0e-6_kdkind) error stop 'nearest distance'
      print '(i5,f12.7)', index, nearest(i)%dis
   end do
   radius2 = 0.08_kdkind
   call kdtree2_r_nearest(tree, query, radius2, found, n, within)
   if (found /= count(direct <= radius2)) error stop 'radius count'
   do i = 1, found
      index = within(i)%idx
      if (index < 1 .or. index > n) error stop 'radius index'
      if (direct(index) > radius2) error stop 'radius membership'
      if (abs(within(i)%dis-direct(index)) > 1.0e-6_kdkind) error stop 'radius distance'
      do j = 1, i-1
         if (within(j)%idx == index) error stop 'duplicate neighbor'
      end do
   end do
   print '(a,i0)', 'Neighbors within squared radius 0.08: ', found
   call kdtree2_destroy(tree)
   print '(a)', 'Checked against an independent direct search; upstream single precision.'
   print '(a)', 'PASS kdtree2'
end program main
