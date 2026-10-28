! Solve Laplacian(u) = -2*pi**2*sin(pi*x)*sin(pi*y) on the unit square.
! Zero Dirichlet boundaries; exact solution u = sin(pi*x)*sin(pi*y).
program demo_fishpack
   use fishpack, only: wp, ip, hwscrt
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer(ip), parameter :: n=32
   real(wp) :: f(n+1,n+1), exact(n+1,n+1), boundary(n+1), pi, x, y, perturbation, err
   integer(ip) :: i,j,status
   pi = acos(-1._wp)
   boundary = 0
   f = 0
   do j=1,n+1
      y = real(j-1,wp)/n
      do i=1,n+1
         x = real(i-1,wp)/n
         exact(i,j) = sin(pi*x)*sin(pi*y)
         if (i>1 .and. i<n+1 .and. j>1 .and. j<n+1) f(i,j) = -2*pi*pi*exact(i,j)
      end do
   end do
   call hwscrt(0._wp,1._wp,n,1_ip,boundary,boundary,0._wp,1._wp,n,1_ip, &
      boundary,boundary,0._wp,f,n+1,perturbation,status)
   if (status/=0) error stop 'Poisson solver failed'
   if (.not. all(ieee_is_finite(f))) error stop 'Nonfinite solution'
   err = maxval(abs(f-exact))
   print '(a,i0,a,i0)', 'Grid intervals: ',n,' x ',n
   print '(a,f16.10)', 'Computed center value: ',f(n/2+1,n/2+1)
   print '(a,es12.3)', 'Maximum discretization error: ',err
   if (err>1e-3_wp) error stop 'Poisson error exceeds second-order tolerance'
   print '(a)', 'PASS fishpack'
end program
