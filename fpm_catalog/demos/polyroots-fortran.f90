program main
   use polyroots_module, only: polyroots, wp => polyroots_module_rk
   implicit none
   integer, parameter :: degree=3
   real(wp) :: coefficients(4)=[1._wp,-6._wp,11._wp,-6._wp]
   real(wp) :: re(degree), im(degree), residual, expected
   complex(wp) :: z, value
   integer :: status, i, j
   ! x**3 - 6*x**2 + 11*x - 6 has roots 1, 2, 3.
   call polyroots(degree,coefficients,re,im,status)
   if (status /= 0) error stop 'root solver failed'
   do i=1,degree
      z=cmplx(re(i),im(i),kind=wp); value=cmplx(coefficients(1),0._wp,kind=wp)
      do j=2,degree+1
         value=value*z+coefficients(j)
      end do
      residual=abs(value)
      if (residual > 1.e-10_wp) error stop 'large polynomial residual'
      print *, 'Root and residual:',z,residual
   end do
   do j=1,3
      expected=real(j,wp)
      if (minval(abs(cmplx(re,im,kind=wp)-expected)) > 1.e-10_wp) error stop 'missing root'
   end do
   print *, 'PASS polyroots-fortran'
end program main
