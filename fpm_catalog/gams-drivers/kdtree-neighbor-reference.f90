! Independent API consumer; MIT: licenses/spatial-nufft-drivers-MIT.txt.
program neighbor_reference
   use kdtree2_precision_module, only: kdkind
   use kdtree2_module, only: kdtree2, kdtree2_result, kdtree2_create, kdtree2_destroy, &
      kdtree2_n_nearest, kdtree2_r_nearest
   use, intrinsic :: iso_fortran_env, only: real64
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer, parameter :: n = 48, counts(*) = [1,5,n], dp = real64
   real(kdkind), target :: points(3,n)
   real(kdkind) :: queries(3,3), radius2(3)
   real(dp) :: distances(n), sorted(n), difference, temp
   type(kdtree2), pointer :: tree
   type(kdtree2_result) :: nearest(n), within(n)
   logical :: seen(n), rearrange
   integer :: i,j,d,q,mode,c,k,r,found,index,calls
   do i = 1,n
      points(:,i) = real([mod(7*i,53),mod(11*i,59),mod(13*i,61)],kdkind)/64
   end do
   queries(:,1) = [13._kdkind,29._kdkind,41._kdkind]/64
   queries(:,2) = 0._kdkind
   queries(:,3) = points(:,17)
   radius2 = [0._kdkind,.125_kdkind,4._kdkind]
   calls = 0
   do mode = 0,1
      rearrange = mode == 1
      tree => kdtree2_create(points,sort=.true.,rearrange=rearrange)
      if (.not. associated(tree)) error stop 'tree allocation'
      do q = 1,3
         distances = 0._dp
         do i = 1,n
            do d = 1,3
               difference = real(points(d,i),dp)-real(queries(d,q),dp)
               distances(i) = distances(i)+difference*difference
            end do
         end do
         ! Independent insertion sort of exhaustive squared distances; tied indexes may differ.
         sorted = distances
         do i = 2,n
            temp = sorted(i)
            j = i-1
            do while (j >= 1)
               if (sorted(j) <= temp) exit
               sorted(j+1) = sorted(j)
               j = j-1
            end do
            sorted(j+1) = temp
         end do
         do c = 1,size(counts)
            k = counts(c)
            call kdtree2_n_nearest(tree,queries(:,q),k,nearest(:k))
            seen = .false.
            do i = 1,k
               index = nearest(i)%idx
               if (index < 1 .or. index > n) error stop 'nearest index range'
               if (seen(index)) error stop 'duplicate nearest index'
               seen(index) = .true.
               if (.not. ieee_is_finite(nearest(i)%dis)) error stop 'nonfinite nearest distance'
               if (abs(real(nearest(i)%dis,dp)-distances(index)) > 1.e-6_dp) error stop 'distance reference'
               if (abs(distances(index)-sorted(i)) > 1.e-6_dp) error stop 'exhaustive nearest ordering'
            end do
            calls = calls+1
         end do
         do r = 1,size(radius2)
            call kdtree2_r_nearest(tree,queries(:,q),radius2(r),found,n,within)
            if (found < 0 .or. found > n) error stop 'radius result count range'
            if (found /= count(distances <= real(radius2(r),dp))) error stop 'exhaustive radius count'
            seen = .false.
            do i = 1,found
               index = within(i)%idx
               if (index < 1 .or. index > n) error stop 'radius index range'
               if (seen(index)) error stop 'duplicate radius index'
               seen(index) = .true.
               if (distances(index) > real(radius2(r),dp)) error stop 'radius membership'
               if (.not. ieee_is_finite(within(i)%dis)) error stop 'nonfinite radius distance'
               if (abs(real(within(i)%dis,dp)-distances(index)) > 1.e-6_dp) error stop 'radius distance'
            end do
            if (any(seen .neqv. (distances <= real(radius2(r),dp)))) error stop 'complete radius set'
            calls = calls+1
         end do
         print '(a,l1,a,i0,a)', 'Rearrange=',rearrange,', query ',q,': nearest and complete radius sets checked.'
      end do
      call kdtree2_destroy(tree)
   end do
   if (calls /= 36) error stop 'search count'
   print '(a)', '36 searches checked against exhaustive real64 distances; upstream tree uses single precision.'
   print '(a)', 'PASS kdtree-neighbor-reference'
end program neighbor_reference
