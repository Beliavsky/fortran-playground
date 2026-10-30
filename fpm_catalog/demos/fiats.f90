! Based on Fiats 0.12.0's write-read-infer example, with known network weights.
! Copyright (c), The Regents of the University of California.
! See docs/fpm-candidates/fiats/licenses/LICENSE.txt for the upstream terms.
program main
   use inference_engine_m, only: inference_engine_t, tensor_t, rkind
   use julienne_string_m, only: string_t
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   type(inference_engine_t) :: network
   type(tensor_t) :: inputs, outputs
   real(rkind), allocatable :: values(:)
   real(rkind) :: expected(2), weights(2,2,2), biases(2,2)
   integer :: i

   weights(:,:,1) = reshape([2.0_rkind, 0.0_rkind, 0.0_rkind, 3.0_rkind], [2,2])
   weights(:,:,2) = reshape([1.0_rkind, 0.0_rkind, 0.0_rkind, 1.0_rkind], [2,2])
   biases(:,1) = [1.0_rkind, -1.0_rkind]
   biases(:,2) = 0.0_rkind
   network = inference_engine_t( &
      metadata=[string_t('Known weights'), string_t('Playground'), string_t('2026-10-29'), &
                string_t('relu'), string_t('false')], weights=weights, biases=biases, nodes=[2,2,2])
   if (network%num_inputs() /= 2 .or. network%num_outputs() /= 2) error stop 'network dimensions'
   do i=-1, 2
      inputs = tensor_t([real(i,rkind), real(i,rkind)])
      outputs = network%infer(inputs)
      values = outputs%values()
      expected = max(0.0_rkind, [2.0_rkind*i+1.0_rkind, 3.0_rkind*i-1.0_rkind])
      if (size(values) /= 2) error stop 'output dimensions'
      if (.not. all(ieee_is_finite(values))) error stop 'nonfinite inference'
      if (maxval(abs(values-expected)) > 1e-5_rkind) error stop 'inference mismatch'
      print '(a,i3,a,2f10.5)', 'Input pair: ', i, '  predicted outputs: ', values
   end do
   print *, 'PASS fiats'
end program
