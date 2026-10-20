! Example: Procedures: internal functions
! Try changing the data or passing x(2:4) to the function.
program internal_functions
   use, intrinsic :: iso_fortran_env, only: real64
   implicit none
   real(real64) :: x(4) = [1,2,3,4]
   print '(a,f10.6)', 'Root mean square: ', rms(x)
contains
   function rms(values) result(value)
      real(real64), intent(in) :: values(:)
      real(real64) :: value
      value = sqrt(sum(values**2)/size(values))
   end function rms
end program internal_functions
