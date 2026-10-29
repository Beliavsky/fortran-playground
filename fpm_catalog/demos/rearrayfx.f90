program growable_matrix
   use iso_fortran_env, only: real64
   use rearrayfx, only: rearray_real64_r2
   implicit none
   integer :: i
   block
      type(rearray_real64_r2) :: matrix
      real(real64) :: expected(2,6)
      matrix%overprov = 2.0
      expected = reshape([(real(i,real64),i=1,12)], [2,6])
      call matrix%allocate([2,2])
      matrix%view = expected(:,1:2)
      ! This growth fits in the spare capacity; existing elements survive.
      call matrix%allocate([2,3])
      if (any(matrix%view(:,1:2)/=expected(:,1:2))) error stop 'First growth lost data'
      matrix%view(:,3) = expected(:,3)
      ! This growth needs a new backing allocation.
      call matrix%allocate([2,6])
      if (any(matrix%view(:,1:3)/=expected(:,1:3))) error stop 'Reallocation lost data'
      matrix%view(:,4:6) = expected(:,4:6)
      print '(a,2i4)', 'Final matrix shape: ', shape(matrix%view)
      print '(a,f8.1)', 'Sum of preserved and appended elements: ', sum(matrix%view)
      if (any(matrix%view/=expected)) error stop 'Matrix data mismatch'
      call matrix%allocate([2,1])
      if (any(matrix%view/=expected(:,1:1))) error stop 'Shrink lost data'
      matrix = expected(:,1:2)
      if (any(matrix%view/=expected(:,1:2))) error stop 'Array assignment failed'
   end block
   print *, 'PASS rearrayfx'
end program growable_matrix
