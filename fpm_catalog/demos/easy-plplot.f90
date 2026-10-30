! Use a file driver so the playground can display the PNG without a GUI.
program main
   use easy_plplot_m
   implicit none
   integer, parameter :: n = 201
   real(wp) :: x(n), sine(n), cosine(n), pi
   logical :: exists
   integer :: bytes
   pi = acos(-1.0_wp)
   x = linspace(0.0_wp, 2.0_wp*pi, n)
   sine = sin(x)
   cosine = cos(x)
   call setup(device='pngcairo', fileName='trigonometry-%n.png', figSize=[800,500])
   call figure()
   call subplot(1, 1, 1)
   call xylim([0.0_wp,2.0_wp*pi], [-1.1_wp,1.1_wp])
   call plot(x, sine, lineColor='b', lineWidth=2.0_wp)
   call plot(x, cosine, lineColor='r', lineWidth=2.0_wp)
   call ticks()
   call labels('x', 'y', 'Sine (blue) and cosine (red)')
   call show()
   inquire(file='trigonometry-1.png', exist=exists, size=bytes)
   if (.not. exists) error stop 'Plot was not created'
   if (bytes < 1000) error stop 'Plot file is unexpectedly small'
   print '(a,i0,a)', 'Created trigonometry-1.png (', bytes, ' bytes)'
   print '(a)', 'PASS easy-plplot'
end program main
