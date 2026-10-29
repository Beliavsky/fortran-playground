program repeated_probe
   use iso_fortran_env, only: dp=>real64
   use simplify, only: perpendicular_distance
   implicit none
   real(dp) :: line(3,2),corner(3,2)
   real(dp),allocatable :: first(:,:),second(:,:)
   line(:,1)=[0._dp,1._dp,2._dp];line(:,2)=0._dp
   corner(:,1)=[0._dp,1._dp,1._dp];corner(:,2)=[0._dp,0._dp,1._dp]
   first=perpendicular_distance(line,0.1_dp)
   if(size(first,1)/=2) error stop 'First call did not reduce line to two endpoints'
   second=perpendicular_distance(corner,0.1_dp)
   print *, 'Second call expected 3 points, actual:',size(second,1)
   if(size(second,1)/=3) error stop 'Repeated call lost corner or endpoints'
   print *, 'PASS repeated perpendicular distance'
end program
