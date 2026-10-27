program main
   use io_fortran_lib, only: to_file, from_file
   implicit none
   real, allocatable :: loaded(:,:)
   real :: values(2,3)
   integer :: status
   values = reshape([1.0,2.0,3.0,4.0,5.0,6.0],[2,3])
   call to_file(values,'samples.csv',delim=',',stat=status)
   if (status /= 0) error stop 'CSV write failed'
   call from_file('samples.csv',into=loaded,delim=',',stat=status)
   if (status /= 0) error stop 'CSV read failed'
   if (any(shape(loaded) /= shape(values))) error stop 'incorrect dimensions'
   if (maxval(abs(loaded-values)) > 1.e-6) error stop 'incorrect CSV values'
   print *, 'Round trip of a 2-by-3 numeric CSV table:'
   print *, loaded
   print *, 'PASS io-fortran-library'
end program main
