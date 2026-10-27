program main
   use regridpack_module, only: regrid
   use iso_fortran_env, only: wp => real64
   implicit none
   real(wp) :: x(3), y(3), targets(2), values(2)
   integer :: status
   x = [0.0_wp,1.0_wp,2.0_wp]
   y = 2*x+1
   targets = [0.25_wp,1.75_wp]
   call regrid(x,y,targets,values,1,status)
   if (status /= 0 .or. maxval(abs(values-(2*targets+1))) > 1.e-12_wp) error stop 'incorrect regrid'
   print *, 'Values on the new grid:', values
   print *, 'PASS regridpack'
end program
