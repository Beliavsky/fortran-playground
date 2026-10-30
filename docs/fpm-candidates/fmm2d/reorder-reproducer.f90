program main
 implicit none
 integer :: order(3) = [3,1,2]
 double precision :: a(2,3), b(2,3)
 a = reshape([1d0,2d0,3d0,4d0,5d0,6d0], [2,3])
 call dreorderi(2,3,a,b,order)
 if (any(b /= reshape([3d0,4d0,5d0,6d0,1d0,2d0],[2,3]))) error stop 'Incorrect permutation'
 print *, 'PASS checked inverse reorder'
end program main
