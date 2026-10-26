module equations
   use minpack_module, only: wp
   implicit none
contains
   subroutine residual(n, x, fvec, iflag)
      integer, intent(in) :: n
      real(wp), intent(in) :: x(n)
      real(wp), intent(out) :: fvec(n)
      integer, intent(inout) :: iflag
      fvec = [x(1)**2-2.0_wp, x(2)-3.0_wp]
   end subroutine
end module
program main
   use minpack_module, only: hybrd1
   use equations
   implicit none
   real(wp) :: x(2), fvec(2), work(19)
   integer :: status
   x = [1.0_wp,1.0_wp]
   call hybrd1(residual, 2, x, fvec, 1.e-10_wp, status, work, size(work))
   if (status /= 1 .or. maxval(abs(fvec)) > 1.e-8_wp) error stop 'nonlinear solve failed'
   print *, 'Solution (sqrt(2), 3):', x
   print *, 'PASS minpack'
end program main
