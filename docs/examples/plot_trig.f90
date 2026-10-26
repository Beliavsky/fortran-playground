program plot_trig
   use iso_fortran_env, only: dp => real64
   use pyplot_module, only: pyplot
   implicit none
   type(pyplot) :: plt
   integer :: i, status
   real(dp) :: x(101)
   real(dp), parameter :: pi = acos(-1.0_dp)

   x = [(2*pi*i/100, i = 0, 100)]
   call plt%initialize(grid=.true., legend=.true., &
      title='Sine and cosine', xlabel='x (radians)', &
      ylabel='Function value', use_oo_api=.true.)
   call plt%add_plot(x, sin(x), label='sin(x)', linestyle='b-')
   call plt%add_plot(x, cos(x), label='cos(x)', linestyle='r--')
   call plt%savefig('trig.png', istat=status)
   if (status /= 0) error stop 'Plot generation failed'
   print '(a)', 'Saved trig.png'
end program plot_trig
