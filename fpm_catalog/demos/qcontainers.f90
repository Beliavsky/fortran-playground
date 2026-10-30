! Integer vectors and string-keyed maps, following the upstream tutorials.
program main
   use qvector_m, only: qvector_t, QVECTOR_RESIZE_LINEAR
   use qhashtbl_m, only: qhashtbl_t
   implicit none
   integer :: i, value, values(5)
   logical :: found
   ! Block scope invokes finalizers for both C-backed containers.
   block
      type(qvector_t) :: vector
      type(qhashtbl_t) :: table
      call vector%new(2, storage_size(i)/8, QVECTOR_RESIZE_LINEAR)
      do i = 1, 5
         call vector%addlast(i, found)
         if (.not. found) error stop 'vector append failed'
      end do
      if (vector%size() /= 5) error stop 'vector growth failed'
      call vector%getat(3, value, found)
      if (.not. found .or. value /= 3) error stop 'vector indexing failed'
      call vector%setat(5, 50, found)
      if (.not. found) error stop 'vector replacement failed'
      call vector%toarray(values)
      if (any(values /= [1, 2, 3, 4, 50])) error stop 'vector contents failed'
      print '(a,5i4)', 'Vector: ', values
      call vector%popfirst(value, found)
      if (.not. found .or. value /= 1) error stop 'vector pop failed'
      if (vector%size() /= 4) error stop 'vector pop size failed'
      call table%new(range=10, size_data=storage_size(value)/8)
      call table%put('red', 10, success=found)
      if (.not. found) error stop 'map insertion failed'
      call table%put('blue', 20, success=found)
      if (.not. found) error stop 'map insertion failed'
      call table%put('red', 30, success=found)
      if (.not. found) error stop 'map replacement failed'
      call table%get('red', value, found)
      if (.not. found .or. value /= 30) error stop 'map lookup failed'
      print '(a,i0)', 'Map red: ', value
      call table%get('missing', value, found)
      if (found) error stop 'missing key reported present'
      call vector%clear()
      call table%clear()
      if (vector%size() /= 0 .or. table%size() /= 0) error stop 'clear failed'
   end block
   print '(a)', 'PASS qcontainers'
end program main
