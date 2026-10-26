module integrand
   use iso_fortran_env, only: wp => real64
   implicit none
contains
   function square(x) result(y)
      real(wp), intent(in) :: x
      real(wp) :: y
      y = x*x
   end function
end module
program main
   use quadpack, only: dqag
   use integrand, only: square, wp
   implicit none
   integer, parameter :: limit=100
   integer :: neval, status, last, iwork(limit)
   real(wp) :: value, error, work(4*limit)
   call dqag(square, 0.0_wp, 1.0_wp, 1.e-10_wp, 1.e-10_wp, 1, &
      value, error, neval, status, limit, 4*limit, last, iwork, work)
   print *, 'Integral, error estimate, status:', value, error, status
   if (status /= 0 .or. abs(value-1.0_wp/3) > 1.e-10_wp) error stop 'incorrect integral'
   print *, 'Integral of x squared:', value
   print *, 'PASS quadpack'
end program main
