program dense_inference
   use iso_fortran_env, only: real32
   use ieee_arithmetic, only: ieee_is_finite
   use athena, only: full_layer_type, array_type
   implicit none
   type(full_layer_type) :: layer
   type(array_type) :: input(1,1)
   real(real32) :: weights(2,3), bias(2), x(3,1), reference(2)
   ! Deterministic inference: no data files, training loop or random weights.
   weights = reshape([1.,-1.,2.,0.5,-0.5,3.], [2,3])
   bias = [0.25_real32,-0.75_real32]
   x(:,1) = [1.,2.,-1.]
   layer = full_layer_type(num_inputs=3, num_outputs=2, activation='tanh')
   layer%params(1)%val(:,1) = reshape(weights,[6])
   layer%params(2)%val(:,1) = bias
   call input(1,1)%allocate(source=x)
   call layer%forward(input)
   reference = tanh(matmul(weights,x(:,1))+bias)
   if (.not.all(ieee_is_finite(layer%output(1,1)%val))) error stop 'Nonfinite output'
   if (maxval(abs(layer%output(1,1)%val(:,1)-reference))>2.e-6_real32) &
      error stop 'Dense layer does not match direct Fortran calculation'
   print '(a)', 'Fully connected layer: 3 inputs, 2 outputs, tanh activation'
   print '(a,2f12.7)', 'Athena inference: ', layer%output(1,1)%val(:,1)
   print '(a,2f12.7)', 'Direct reference: ', reference
   print *, 'PASS athena'
end program dense_inference
