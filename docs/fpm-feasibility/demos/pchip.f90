! Interpolate linear data and verify an interior value.
program demo
   use iso_fortran_env, only: wp => real64
   use ieee_arithmetic, only: ieee_is_finite
   use pchip_module, only: dpchim, dpchfe
   implicit none
   real(wp) :: x(3), f(1,3), d(1,3), query(1), answer(1)
   integer :: status
   logical :: skip
   x = [0.0_wp, 1.0_wp, 2.0_wp]
   f(1,:) = 2*x + 1
   call dpchim(3, x, f, d, 1, status)
   if (status < 0) error stop 'derivative calculation failed'
   skip = .false.
   query = 0.5_wp
   call dpchfe(3, x, f, d, 1, skip, 1, query, answer, status)
   if (.not. ieee_is_finite(answer(1))) error stop 'nonfinite interpolation'
   if (status < 0 .or. abs(answer(1) - 2.0_wp) > 1.0e-12_wp) error stop 'incorrect interpolation'
   print '(a,f8.4)', 'PASS pchip value=', answer(1)
end program demo
