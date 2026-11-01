! Independent consumer probe; expected requested bounds are 0 <= x <= 1.
program main
   use iso_fortran_env, only: real64
   use ieee_arithmetic, only: ieee_is_finite
   use fortran_test_helper, only: create_random_array
   implicit none
   integer,allocatable :: seed(:)
   integer :: n
   real(real64) :: x(64)
   call random_seed(size=n)
   allocate(seed(n),source=137)
   call random_seed(put=seed)
   call create_random_array(x,xmin=0._real64,xmax=1._real64)
   print '(a,2f14.9)', 'Requested [0,1]; observed min/max: ',minval(x),maxval(x)
   if(.not.all(ieee_is_finite(x))) error stop 'Nonfinite values'
   if(any(x<0._real64).or.any(x>1._real64)) error stop 'Requested bounds violated'
   print '(a)', 'PASS requested bounds'
end program
