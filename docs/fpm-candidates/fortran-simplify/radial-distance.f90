program radial_probe
   use iso_fortran_env, only: dp=>real64
   use simplify, only: radial_distance
   implicit none
   real(dp) :: curve(3,2)
   real(dp),allocatable :: result(:,:)
   curve(:,1)=[10._dp,10.01_dp,11._dp]
   curve(:,2)=10._dp
   result=radial_distance(curve,0.1_dp)
   print *, 'Expected 2 points, actual:',size(result,1)
   if(size(result,1)/=2) error stop 'Near-duplicate interior point was not removed'
   print *, 'PASS radial distance'
end program
