program simplify_curve
   ! This pin has upstream limitations in radial_distance and in repeated
   ! perpendicular_distance calls. This example makes one perpendicular call.
   ! Reproducers: docs/fpm-candidates/fortran-simplify in the playground repo.
   use iso_fortran_env, only: dp => real64
   use ieee_arithmetic, only: ieee_is_finite
   use simplify, only: perpendicular_distance
   use pyplot_module, only: pyplot
   implicit none
   integer, parameter :: n=251
   real(dp), parameter :: pi=acos(-1.0_dp), tolerance=0.005_dp
   real(dp) :: curve(n,2), fraction, interpolated, max_error
   real(dp), allocatable :: reduced(:,:)
   type(pyplot) :: plot
   integer :: i, j, status
   curve(:,1) = [(2*pi*(i-1)/(n-1),i=1,n)]
   curve(:,2) = sin(curve(:,1))
   ! One pass of perpendicular-distance simplification.
   reduced = perpendicular_distance(curve, tolerance)
   if (.not.all(ieee_is_finite(reduced))) error stop 'Nonfinite coordinates'
   if (size(reduced,1)>=n .or. size(reduced,1)<2) error stop 'Unexpected point count'
   if (any(reduced(1,:)/=curve(1,:))) error stop 'First endpoint lost'
   if (any(reduced(size(reduced,1),:)/=curve(n,:))) error stop 'Last endpoint lost'
   max_error = 0
   j = 1
   do i=1,n
      do while (j<size(reduced,1)-1)
         if (curve(i,1)<=reduced(j+1,1)) exit
         j = j+1
      end do
      fraction = (curve(i,1)-reduced(j,1))/(reduced(j+1,1)-reduced(j,1))
      interpolated = (1-fraction)*reduced(j,2)+fraction*reduced(j+1,2)
      max_error = max(max_error,abs(curve(i,2)-interpolated))
   end do
   if (max_error>tolerance) error stop 'Independent interpolation check failed'
   print '(a,i0,a,i0)', 'Sine curve: ',n,' points reduced to ',size(reduced,1)
   print '(a,es12.4)', 'Maximum vertical interpolation error: ',max_error
   call plot%initialize(grid=.true.,legend=.true.,title='Polyline simplification', &
      xlabel='x',ylabel='sin(x)',use_oo_api=.true.)
   call plot%add_plot(curve(:,1),curve(:,2),label='Original',linestyle='b-')
   call plot%add_plot(reduced(:,1),reduced(:,2),label='Simplified',linestyle='r.')
   call plot%savefig('simplified.png',istat=status)
   if (status/=0) error stop 'Plot generation failed'
   print *, 'PASS fortran-simplify'
end program simplify_curve
