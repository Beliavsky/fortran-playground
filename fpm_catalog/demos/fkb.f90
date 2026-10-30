! Deterministic inference from a tiny Keras-style text model; no Python needed.
program main
   use mod_kinds, only: rk
   use mod_network, only: network_type
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
   type(network_type) :: network, restored
   real(rk) :: inputs(2,4), weights(2,3), bias(3), hidden(3), expected
   real(rk), allocatable :: prediction(:), again(:)
   integer :: unit, i, status
   weights = reshape([1.0_rk,2.0_rk, -1.0_rk,0.5_rk, 0.25_rk,-2.0_rk], [2,3])
   bias = [1.0_rk,-1.0_rk,0.5_rk]
   inputs = reshape([1.0_rk,2.0_rk, -2.0_rk,0.5_rk, 0.0_rk,0.0_rk, 3.0_rk,-1.0_rk], [2,4])
   open(newunit=unit, file='tiny-network.txt', status='replace', action='write', iostat=status)
   if (status /= 0) error stop 'Model file open failed'
   write(unit, '(a)') '5', 'input 2', 'dense 3', 'relu 0', 'dense 1', 'linear 0', '0.01'
   write(unit, *) bias
   write(unit, *) 0.25_rk
   write(unit, *) weights
   write(unit, *) [2.0_rk,-3.0_rk,0.5_rk]
   close(unit)
   call network%load('tiny-network.txt')
   if (network%input_size /= 2 .or. network%output_size /= 1) error stop 'Network dimensions failed'
   call network%save('saved-network.txt')
   call restored%load('saved-network.txt')
   do i = 1, size(inputs,2)
      hidden = max(0.0_rk, matmul(transpose(weights), inputs(:,i)) + bias)
      expected = dot_product([2.0_rk,-3.0_rk,0.5_rk], hidden) + 0.25_rk
      prediction = network%output(inputs(:,i))
      again = restored%output(inputs(:,i))
      if (size(prediction) /= 1 .or. size(again) /= 1) error stop 'Prediction shape failed'
      if (.not. all(ieee_is_finite(prediction)) .or. .not. all(ieee_is_finite(again))) &
         error stop 'Nonfinite prediction'
      if (abs(prediction(1)-expected) > 1.0e-12_rk) error stop 'Inference mismatch'
      if (abs(again(1)-expected) > 1.0e-12_rk) error stop 'Model save/load mismatch'
      print '(a,2f7.2,a,f10.5)', 'Input: ', inputs(:,i), '  prediction: ', prediction(1)
   end do
   open(newunit=unit, file='tiny-network.txt', status='old')
   close(unit, status='delete')
   open(newunit=unit, file='saved-network.txt', status='old')
   close(unit, status='delete')
   print '(a)', 'PASS fkb'
end program main
