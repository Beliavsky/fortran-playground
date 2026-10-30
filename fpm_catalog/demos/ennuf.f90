! Fixed network: two inputs, two ReLU hidden units, one output.
program main
   use ennuf_example_mod, only: ennuf_example
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   real :: features(1,2), prediction(1,1), inputs(2,4), expected(4)
   integer :: i
   inputs = reshape([1.,2., -2.,1., 0.,0., 2.,-2.], [2,4])
   ! y = 2*max(x1+2*x2+.5,0) - 3*max(-x1+.5*x2-.25,0) + 1
   expected = [12., -4.75, 2., 1.]
   do i = 1, 4
      features(1,:) = inputs(:,i)
      call ennuf_example(features, prediction)
      if (.not. all(ieee_is_finite(prediction))) error stop 'Nonfinite prediction'
      if (abs(prediction(1,1)-expected(i)) > 1.e-6) error stop 'Incorrect prediction'
      print '(a,2f8.2,a,f9.4)', 'Input: ', features, '  prediction: ', prediction
   end do
   print '(a)', 'PASS ennuf'
end program main
