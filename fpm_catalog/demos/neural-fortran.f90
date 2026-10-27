program main
   use nf, only: network, input, dense, linear, sgd
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   type(network) :: net
   integer :: nseed, epoch, i
   integer, allocatable :: seed(:)
   real :: x, target, prediction(1), max_error
   call random_seed(size=nseed)
   allocate(seed(nseed)); seed=42; call random_seed(put=seed)
   net = network([input(1), dense(1, activation=linear())])
   ! Learn y = 2*x + 1 from nine generated observations.
   do epoch=1,150
      do i=-4,4
         x=real(i)/4; target=2*x+1
         call net%forward([x])
         call net%backward([target])
         call net%update(sgd(learning_rate=0.05))
      end do
   end do
   max_error=0
   do i=-5,5
      x=real(i)/5; prediction=net%predict([x])
      if (.not.all(ieee_is_finite(prediction))) error stop 'nonfinite prediction'
      max_error=max(max_error,abs(prediction(1)-(2*x+1)))
   end do
   if (max_error > 1.e-4) error stop 'network did not learn the line'
   print *, 'Learned y = 2*x + 1; maximum test error:', max_error
   print *, 'PASS neural-fortran'
end program main
