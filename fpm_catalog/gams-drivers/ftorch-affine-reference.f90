! Independent MIT consumer; see licenses/friction-torch-drivers-MIT.txt.
! Reuses the existing playground-owned embedded y=2*x+1 TorchScript fixture as data.
program torch_affine_reference
   use, intrinsic :: iso_fortran_env, only: int8,int32,real32,real64
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   use ftorch, only: torch_model,torch_tensor,torch_kCPU,torch_kFloat32,torch_kFloat64, &
      torch_model_load,torch_tensor_from_array,torch_model_forward,torch_delete
   implicit none
   character(*), parameter :: model_hex = &
      '504b0304000008080000000000000000000000000000000000000d00150074696e792f646174612e706b6c464211005a' // &
      '5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a8002635f5f746f7263685f5f0a54696e790a710029817d28756271012e504b07' // &
      '08251e06571d0000001d000000504b03040000080800000000000000000000000000000000000016001f0074696e792f' // &
      '636f64652f5f5f746f7263685f5f2e707946421b005a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a' // &
      '636c6173732054696e79284d6f64756c65293a0a20205f5f706172616d65746572735f5f203d205b5d0a20205f5f6275' // &
      '66666572735f5f203d205b5d0a202064656620666f72776172642873656c663a205f5f746f7263685f5f2e54696e792c' // &
      '0a20202020783a2054656e736f7229202d3e2054656e736f723a0a2020202072657475726e20746f7263682e61646428' // &
      '746f7263682e6d756c28782c20322e292c20312e290a504b07080999260aa6000000a6000000504b0304140008080800' // &
      '0000000000000000000000000000000020000c0074696e792f636f64652f5f5f746f7263685f5f2e70792e6465627567' // &
      '5f706b6c464208005a5a5a5a5a5a5a5a4d8dcb4a03311486333355eb3c80e82e2e84682554972242052fe5788171c06c' // &
      '24e84cc64487a9c9a4d8a52bb3f50544117d4f932eda1e0efc1fff77e0bcc56c1d21747a9d5d0e727e3bcccff94d9e0d' // &
      'afce783e38be38d18830af918ed89a8f5254b81a99d77b539256d4d52e9e6c1fa43a661b5e623f46d8b169f004efe07d' // &
      'dac73dbc47fba94e58d7fbc3d61ad53c1ee98ed54b04506147a690f44959ca5f54f15c8bf461acea92abc6d6aab5a95e' // &
      '267744d80c1020a757a611f65d060111c480824e2072ba0b9b409d27f890818983d8c1a7e7adc08983af85fe5bceef7f' // &
      '3cf702771cfc2ef47f72f6d2ea5547ff01504b0708c50726c5f10000002b010000504b03040000080800000000000000' // &
      '000000000000000000000012000f0074696e792f636f6e7374616e74732e706b6c46420b005a5a5a5a5a5a5a5a5a5a5a' // &
      '8002292e504b07086d2f09570400000004000000504b0304000008080000000000000000000000000000000000000c00' // &
      '420074696e792f76657273696f6e46423e005a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a' // &
      '5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a330a504b0708d19e6755020000000200' // &
      '0000504b0304000008080000000000000000000000000000000000000e00420074696e792f627974656f726465724642' // &
      '3e005a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a' // &
      '5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a6c6974746c65504b0708853de3190600000006000000504b0304000008080000' // &
      '000000000000000000000000000000001b00310074696e792f2e646174612f73657269616c697a6174696f6e5f696446' // &
      '422d005a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a' // &
      '30303533313637383035313134313633393835333034373032333734323236343535383835333533504b07082c0b8d73' // &
      '2800000028000000504b0102000000000808000000000000251e06571d0000001d0000000d0000000000000000000000' // &
      '00000000000074696e792f646174612e706b6c504b01020000000008080000000000000999260aa6000000a600000016' // &
      '000000000000000000000000006d00000074696e792f636f64652f5f5f746f7263685f5f2e7079504b01020000140008' // &
      '08080000000000c50726c5f10000002b01000020000000000000000000000000007601000074696e792f636f64652f5f' // &
      '5f746f7263685f5f2e70792e64656275675f706b6c504b01020000000008080000000000006d2f095704000000040000' // &
      '001200000000000000000000000000c102000074696e792f636f6e7374616e74732e706b6c504b010200000000080800' // &
      '0000000000d19e675502000000020000000c000000000000000000000000001403000074696e792f76657273696f6e50' // &
      '4b0102000000000808000000000000853de31906000000060000000e000000000000000000000000009203000074696e' // &
      '792f627974656f72646572504b01020000000008080000000000002c0b8d7328000000280000001b0000000000000000' // &
      '00000000001604000074696e792f2e646174612f73657269616c697a6174696f6e5f6964504b06062c00000000000000' // &
      '1e032d00000000000000000007000000000000000700000000000000cc01000000000000b804000000000000504b0607' // &
      '00000000840600000000000001000000504b05060000000007000700cc010000b80400000000'
   integer(int8) :: bytes(len(model_hex)/2)
   integer :: i,j,k,value,unit,batch,sample,configurations,calls,entries
   character(2) :: hex_byte
   real(real64) :: worst,error
   type(torch_model) :: model
   type(torch_tensor) :: inputs(1),outputs(1)
   do i=1,size(bytes)
      hex_byte=model_hex(2*i-1:2*i); read(hex_byte,'(z2)') value
      if (value>127) value=value-256
      bytes(i)=int(value,int8)
   end do
   open(newunit=unit,file='affine.pt',access='stream',form='unformatted',status='replace')
   write(unit) bytes; close(unit)
   call torch_model_load(model,'affine.pt',torch_kCPU)
   configurations=0; calls=0; entries=0; worst=0
   block
      real(real32), target :: x(7),y(7)
      real(real32) :: saved(7),first(7)
      call torch_tensor_from_array(inputs(1),x,torch_kCPU)
      call torch_tensor_from_array(outputs(1),y,torch_kCPU)
      if (inputs(1)%rank()/=1) error stop 'input tensor rank'
      if (any(inputs(1)%shape()/=[7])) error stop 'input tensor shape'
      if (any(inputs(1)%stride()/=[1])) error stop 'input tensor strides'
      if (inputs(1)%dtype()/=torch_kFloat32) error stop 'input tensor dtype'
      do batch=1,13
         sample=batch; if (batch==13) sample=1
         do i=1,7
            x(i)=real(modulo(sample*(i),37)-18,real32)/8
         end do
         saved=x; y=-huge(y)
         call torch_model_forward(model,inputs,outputs)
         if (any(x/=saved)) error stop 'inference changed input buffer'
         if (.not.all(ieee_is_finite(y))) error stop 'nonfinite tensor prediction'
         do i=1,7
            error=abs(real(y(i),real64)-(2*real(saved(i),real64)+1))
            if (error/=0) error stop 'exact dyadic affine tensor reference'
            worst=max(worst,error); entries=entries+1
         end do
         if (batch==1) first=y
         if (batch==13 .and. any(y/=first)) error stop 'repeated tensor inference differs'
         calls=calls+1
      end do
      call torch_delete(inputs); call torch_delete(outputs)
      configurations=configurations+1
   end block
   block
      real(real32), target :: x(2,3),y(2,3)
      real(real32) :: saved(2,3),first(2,3)
      call torch_tensor_from_array(inputs(1),x,torch_kCPU)
      call torch_tensor_from_array(outputs(1),y,torch_kCPU)
      if (inputs(1)%rank()/=2) error stop 'input tensor rank'
      if (any(inputs(1)%shape()/=[2,3])) error stop 'input tensor shape'
      if (any(inputs(1)%stride()/=[1,2])) error stop 'input tensor strides'
      if (inputs(1)%dtype()/=torch_kFloat32) error stop 'input tensor dtype'
      do batch=1,13
         sample=batch; if (batch==13) sample=1
         do j=1,3
         do i=1,2
            x(i,j)=real(modulo(sample*(i+7*j),37)-18,real32)/8
         end do
         end do
         saved=x; y=-huge(y)
         call torch_model_forward(model,inputs,outputs)
         if (any(x/=saved)) error stop 'inference changed input buffer'
         if (.not.all(ieee_is_finite(y))) error stop 'nonfinite tensor prediction'
         do j=1,3
         do i=1,2
            error=abs(real(y(i,j),real64)-(2*real(saved(i,j),real64)+1))
            if (error/=0) error stop 'exact dyadic affine tensor reference'
            worst=max(worst,error); entries=entries+1
         end do
         end do
         if (batch==1) first=y
         if (batch==13 .and. any(y/=first)) error stop 'repeated tensor inference differs'
         calls=calls+1
      end do
      call torch_delete(inputs); call torch_delete(outputs)
      configurations=configurations+1
   end block
   block
      real(real32), target :: x(2,3),y(3,2)
      real(real32) :: saved(2,3),first(3,2)
      call torch_tensor_from_array(inputs(1),x,torch_kCPU,permute_dims=[2_int32,1_int32])
      call torch_tensor_from_array(outputs(1),y,torch_kCPU)
      if (inputs(1)%rank()/=2) error stop 'input tensor rank'
      if (any(inputs(1)%shape()/=[3,2])) error stop 'input tensor shape'
      if (any(inputs(1)%stride()/=[2,1])) error stop 'input tensor strides'
      if (inputs(1)%dtype()/=torch_kFloat32) error stop 'input tensor dtype'
      do batch=1,13
         sample=batch; if (batch==13) sample=1
         do j=1,3
         do i=1,2
            x(i,j)=real(modulo(sample*(i+7*j),37)-18,real32)/8
         end do
         end do
         saved=x; y=-huge(y)
         call torch_model_forward(model,inputs,outputs)
         if (any(x/=saved)) error stop 'inference changed input buffer'
         if (.not.all(ieee_is_finite(y))) error stop 'nonfinite tensor prediction'
         do j=1,3
         do i=1,2
            error=abs(real(y(j,i),real64)-(2*real(saved(i,j),real64)+1))
            if (error/=0) error stop 'exact dyadic affine tensor reference'
            worst=max(worst,error); entries=entries+1
         end do
         end do
         if (batch==1) first=y
         if (batch==13 .and. any(y/=first)) error stop 'repeated tensor inference differs'
         calls=calls+1
      end do
      call torch_delete(inputs); call torch_delete(outputs)
      configurations=configurations+1
   end block
   block
      real(real32), target :: x(2,3,4),y(2,3,4)
      real(real32) :: saved(2,3,4),first(2,3,4)
      call torch_tensor_from_array(inputs(1),x,torch_kCPU)
      call torch_tensor_from_array(outputs(1),y,torch_kCPU)
      if (inputs(1)%rank()/=3) error stop 'input tensor rank'
      if (any(inputs(1)%shape()/=[2,3,4])) error stop 'input tensor shape'
      if (any(inputs(1)%stride()/=[1,2,6])) error stop 'input tensor strides'
      if (inputs(1)%dtype()/=torch_kFloat32) error stop 'input tensor dtype'
      do batch=1,13
         sample=batch; if (batch==13) sample=1
         do k=1,4
         do j=1,3
         do i=1,2
            x(i,j,k)=real(modulo(sample*(i+7*j+11*k),37)-18,real32)/8
         end do
         end do
         end do
         saved=x; y=-huge(y)
         call torch_model_forward(model,inputs,outputs)
         if (any(x/=saved)) error stop 'inference changed input buffer'
         if (.not.all(ieee_is_finite(y))) error stop 'nonfinite tensor prediction'
         do k=1,4
         do j=1,3
         do i=1,2
            error=abs(real(y(i,j,k),real64)-(2*real(saved(i,j,k),real64)+1))
            if (error/=0) error stop 'exact dyadic affine tensor reference'
            worst=max(worst,error); entries=entries+1
         end do
         end do
         end do
         if (batch==1) first=y
         if (batch==13 .and. any(y/=first)) error stop 'repeated tensor inference differs'
         calls=calls+1
      end do
      call torch_delete(inputs); call torch_delete(outputs)
      configurations=configurations+1
   end block
   block
      real(real32), target :: x(2,3,4),y(3,4,2)
      real(real32) :: saved(2,3,4),first(3,4,2)
      call torch_tensor_from_array(inputs(1),x,torch_kCPU,permute_dims=[2_int32,3_int32,1_int32])
      call torch_tensor_from_array(outputs(1),y,torch_kCPU)
      if (inputs(1)%rank()/=3) error stop 'input tensor rank'
      if (any(inputs(1)%shape()/=[3,4,2])) error stop 'input tensor shape'
      if (any(inputs(1)%stride()/=[2,6,1])) error stop 'input tensor strides'
      if (inputs(1)%dtype()/=torch_kFloat32) error stop 'input tensor dtype'
      do batch=1,13
         sample=batch; if (batch==13) sample=1
         do k=1,4
         do j=1,3
         do i=1,2
            x(i,j,k)=real(modulo(sample*(i+7*j+11*k),37)-18,real32)/8
         end do
         end do
         end do
         saved=x; y=-huge(y)
         call torch_model_forward(model,inputs,outputs)
         if (any(x/=saved)) error stop 'inference changed input buffer'
         if (.not.all(ieee_is_finite(y))) error stop 'nonfinite tensor prediction'
         do k=1,4
         do j=1,3
         do i=1,2
            error=abs(real(y(j,k,i),real64)-(2*real(saved(i,j,k),real64)+1))
            if (error/=0) error stop 'exact dyadic affine tensor reference'
            worst=max(worst,error); entries=entries+1
         end do
         end do
         end do
         if (batch==1) first=y
         if (batch==13 .and. any(y/=first)) error stop 'repeated tensor inference differs'
         calls=calls+1
      end do
      call torch_delete(inputs); call torch_delete(outputs)
      configurations=configurations+1
   end block
   block
      real(real64), target :: x(7),y(7)
      real(real64) :: saved(7),first(7)
      call torch_tensor_from_array(inputs(1),x,torch_kCPU)
      call torch_tensor_from_array(outputs(1),y,torch_kCPU)
      if (inputs(1)%rank()/=1) error stop 'input tensor rank'
      if (any(inputs(1)%shape()/=[7])) error stop 'input tensor shape'
      if (any(inputs(1)%stride()/=[1])) error stop 'input tensor strides'
      if (inputs(1)%dtype()/=torch_kFloat64) error stop 'input tensor dtype'
      do batch=1,13
         sample=batch; if (batch==13) sample=1
         do i=1,7
            x(i)=real(modulo(sample*(i),37)-18,real64)/8
         end do
         saved=x; y=-huge(y)
         call torch_model_forward(model,inputs,outputs)
         if (any(x/=saved)) error stop 'inference changed input buffer'
         if (.not.all(ieee_is_finite(y))) error stop 'nonfinite tensor prediction'
         do i=1,7
            error=abs(real(y(i),real64)-(2*real(saved(i),real64)+1))
            if (error/=0) error stop 'exact dyadic affine tensor reference'
            worst=max(worst,error); entries=entries+1
         end do
         if (batch==1) first=y
         if (batch==13 .and. any(y/=first)) error stop 'repeated tensor inference differs'
         calls=calls+1
      end do
      call torch_delete(inputs); call torch_delete(outputs)
      configurations=configurations+1
   end block
   block
      real(real64), target :: x(2,3),y(2,3)
      real(real64) :: saved(2,3),first(2,3)
      call torch_tensor_from_array(inputs(1),x,torch_kCPU)
      call torch_tensor_from_array(outputs(1),y,torch_kCPU)
      if (inputs(1)%rank()/=2) error stop 'input tensor rank'
      if (any(inputs(1)%shape()/=[2,3])) error stop 'input tensor shape'
      if (any(inputs(1)%stride()/=[1,2])) error stop 'input tensor strides'
      if (inputs(1)%dtype()/=torch_kFloat64) error stop 'input tensor dtype'
      do batch=1,13
         sample=batch; if (batch==13) sample=1
         do j=1,3
         do i=1,2
            x(i,j)=real(modulo(sample*(i+7*j),37)-18,real64)/8
         end do
         end do
         saved=x; y=-huge(y)
         call torch_model_forward(model,inputs,outputs)
         if (any(x/=saved)) error stop 'inference changed input buffer'
         if (.not.all(ieee_is_finite(y))) error stop 'nonfinite tensor prediction'
         do j=1,3
         do i=1,2
            error=abs(real(y(i,j),real64)-(2*real(saved(i,j),real64)+1))
            if (error/=0) error stop 'exact dyadic affine tensor reference'
            worst=max(worst,error); entries=entries+1
         end do
         end do
         if (batch==1) first=y
         if (batch==13 .and. any(y/=first)) error stop 'repeated tensor inference differs'
         calls=calls+1
      end do
      call torch_delete(inputs); call torch_delete(outputs)
      configurations=configurations+1
   end block
   block
      real(real64), target :: x(2,3),y(3,2)
      real(real64) :: saved(2,3),first(3,2)
      call torch_tensor_from_array(inputs(1),x,torch_kCPU,permute_dims=[2_int32,1_int32])
      call torch_tensor_from_array(outputs(1),y,torch_kCPU)
      if (inputs(1)%rank()/=2) error stop 'input tensor rank'
      if (any(inputs(1)%shape()/=[3,2])) error stop 'input tensor shape'
      if (any(inputs(1)%stride()/=[2,1])) error stop 'input tensor strides'
      if (inputs(1)%dtype()/=torch_kFloat64) error stop 'input tensor dtype'
      do batch=1,13
         sample=batch; if (batch==13) sample=1
         do j=1,3
         do i=1,2
            x(i,j)=real(modulo(sample*(i+7*j),37)-18,real64)/8
         end do
         end do
         saved=x; y=-huge(y)
         call torch_model_forward(model,inputs,outputs)
         if (any(x/=saved)) error stop 'inference changed input buffer'
         if (.not.all(ieee_is_finite(y))) error stop 'nonfinite tensor prediction'
         do j=1,3
         do i=1,2
            error=abs(real(y(j,i),real64)-(2*real(saved(i,j),real64)+1))
            if (error/=0) error stop 'exact dyadic affine tensor reference'
            worst=max(worst,error); entries=entries+1
         end do
         end do
         if (batch==1) first=y
         if (batch==13 .and. any(y/=first)) error stop 'repeated tensor inference differs'
         calls=calls+1
      end do
      call torch_delete(inputs); call torch_delete(outputs)
      configurations=configurations+1
   end block
   block
      real(real64), target :: x(2,3,4),y(2,3,4)
      real(real64) :: saved(2,3,4),first(2,3,4)
      call torch_tensor_from_array(inputs(1),x,torch_kCPU)
      call torch_tensor_from_array(outputs(1),y,torch_kCPU)
      if (inputs(1)%rank()/=3) error stop 'input tensor rank'
      if (any(inputs(1)%shape()/=[2,3,4])) error stop 'input tensor shape'
      if (any(inputs(1)%stride()/=[1,2,6])) error stop 'input tensor strides'
      if (inputs(1)%dtype()/=torch_kFloat64) error stop 'input tensor dtype'
      do batch=1,13
         sample=batch; if (batch==13) sample=1
         do k=1,4
         do j=1,3
         do i=1,2
            x(i,j,k)=real(modulo(sample*(i+7*j+11*k),37)-18,real64)/8
         end do
         end do
         end do
         saved=x; y=-huge(y)
         call torch_model_forward(model,inputs,outputs)
         if (any(x/=saved)) error stop 'inference changed input buffer'
         if (.not.all(ieee_is_finite(y))) error stop 'nonfinite tensor prediction'
         do k=1,4
         do j=1,3
         do i=1,2
            error=abs(real(y(i,j,k),real64)-(2*real(saved(i,j,k),real64)+1))
            if (error/=0) error stop 'exact dyadic affine tensor reference'
            worst=max(worst,error); entries=entries+1
         end do
         end do
         end do
         if (batch==1) first=y
         if (batch==13 .and. any(y/=first)) error stop 'repeated tensor inference differs'
         calls=calls+1
      end do
      call torch_delete(inputs); call torch_delete(outputs)
      configurations=configurations+1
   end block
   block
      real(real64), target :: x(2,3,4),y(3,4,2)
      real(real64) :: saved(2,3,4),first(3,4,2)
      call torch_tensor_from_array(inputs(1),x,torch_kCPU,permute_dims=[2_int32,3_int32,1_int32])
      call torch_tensor_from_array(outputs(1),y,torch_kCPU)
      if (inputs(1)%rank()/=3) error stop 'input tensor rank'
      if (any(inputs(1)%shape()/=[3,4,2])) error stop 'input tensor shape'
      if (any(inputs(1)%stride()/=[2,6,1])) error stop 'input tensor strides'
      if (inputs(1)%dtype()/=torch_kFloat64) error stop 'input tensor dtype'
      do batch=1,13
         sample=batch; if (batch==13) sample=1
         do k=1,4
         do j=1,3
         do i=1,2
            x(i,j,k)=real(modulo(sample*(i+7*j+11*k),37)-18,real64)/8
         end do
         end do
         end do
         saved=x; y=-huge(y)
         call torch_model_forward(model,inputs,outputs)
         if (any(x/=saved)) error stop 'inference changed input buffer'
         if (.not.all(ieee_is_finite(y))) error stop 'nonfinite tensor prediction'
         do k=1,4
         do j=1,3
         do i=1,2
            error=abs(real(y(j,k,i),real64)-(2*real(saved(i,j,k),real64)+1))
            if (error/=0) error stop 'exact dyadic affine tensor reference'
            worst=max(worst,error); entries=entries+1
         end do
         end do
         end do
         if (batch==1) first=y
         if (batch==13 .and. any(y/=first)) error stop 'repeated tensor inference differs'
         calls=calls+1
      end do
      call torch_delete(inputs); call torch_delete(outputs)
      configurations=configurations+1
   end block
   call torch_delete(model)
   if (configurations/=10 .or. calls/=130 .or. entries/=1742) error stop 'tensor reference counts'
   print '(a)', '10 tensor configurations: REAL32/REAL64, ranks 1/2/3, identity and asymmetric axis permutations.'
   print '(a,i0,a,i0)', 'CPU forward calls: ',calls,'; exact scalar output references: ',entries
   print '(a,es14.5)', 'Maximum absolute affine prediction error: ',worst
   print '(a)', 'In-place input updates and exact replay; input rank/shape/stride/dtype and input immutability checked.'
   print '(a)', 'Existing y=2*x+1 fixture only; nonlinear networks, training, gradients and GPU execution unverified.'
   print '(a)', 'PASS ftorch-affine-reference'
end program
