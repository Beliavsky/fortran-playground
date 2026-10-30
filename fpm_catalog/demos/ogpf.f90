! Headless Gnuplot contours; the PNG is returned to the playground browser.
program main
   use ogpf
   implicit none
   integer, parameter :: n=61
   real(wp) :: axis(n), x(n,n), y(n,n), z(n,n)
   type(gpf) :: plot
   logical :: exists
   integer :: i, j, bytes
   axis = linspace(-3.0_wp, 3.0_wp, n)
   do j = 1, n
      do i = 1, n
         x(i,j) = axis(i)
         y(i,j) = axis(j)
      end do
   end do
   z = exp(-(x*x+y*y))
   call plot%options('set terminal pngcairo size 800,600 font "DejaVu Sans,11"')
   call plot%options('set output "gaussian.png"')
   call plot%title('Contours of exp(-(x**2 + y**2))')
   call plot%xlabel('x')
   call plot%ylabel('y')
   call plot%contour(x, y, z, lspec='with lines linewidth 2 linecolor rgb "#1565c0"')
   inquire(file='gaussian.png', exist=exists, size=bytes)
   if (.not. exists) error stop 'Contour PNG was not created'
   if (bytes < 1000) error stop 'Contour PNG is unexpectedly small'
   print '(a,i0,a)', 'Created gaussian.png (', bytes, ' bytes)'
   print '(a)', 'PASS ogpf'
end program main
