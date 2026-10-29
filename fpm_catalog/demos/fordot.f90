program demo_dot_products
   use kinds, only: rk
   use fordot, only: dot_product
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   real(rk), parameter :: u(*) = [1.0_rk, 2.0_rk, 3.0_rk, 4.0_rk, 5.0_rk, 6.0_rk, 7.0_rk, 8.0_rk]
   real(rk), parameter :: v(*) = [8.0_rk, 7.0_rk, 6.0_rk, 5.0_rk, 4.0_rk, 3.0_rk, 2.0_rk, 1.0_rk]
   character(2), parameter :: methods(*) = ['m1', 'm2', 'm3', 'm4']
   real(rk) :: plain, blocked
   integer :: i

   print '(a)', 'Method      ordinary       three unequal blocks'
   do i = 1, size(methods)
      plain = dot_product(u, v, option=methods(i))
      blocked = dot_product(u, v, option=methods(i), nblock=3)
      if (.not. ieee_is_finite(plain) .or. .not. ieee_is_finite(blocked)) error stop 'nonfinite product'
      if (abs(plain - 120.0_rk) > 1.e-10_rk) error stop 'ordinary dot product'
      if (abs(blocked - 120.0_rk) > 1.e-10_rk) error stop 'blocked dot product'
      print '(a, 2f18.8)', methods(i), plain, blocked
   end do
   print '(a)', 'One process; these correctness checks are not a performance benchmark.'
   print '(a)', 'PASS fordot'
end program demo_dot_products
