! Independent API consumer; MIT: licenses/kriging-network-drivers-MIT.txt.
program network_reference
   use mod_kinds, only: rk
   use mod_network, only: network_type
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   type(network_type) :: original,restored
   real(rk) :: first(2,3),second(3,2),hidden_bias(3),output_bias(2),x(2),hidden(3),expected(2)
   real(rk), allocatable :: prediction(:),again(:)
   integer :: unit,status,i,j,k,l,cases
   first = reshape([1._rk,-2._rk, .5_rk,1.5_rk, -1._rk,.25_rk],[2,3])
   second = reshape([1._rk,.5_rk,-2._rk, -.25_rk,1.5_rk,.75_rk],[3,2])
   hidden_bias = [.5_rk,-.25_rk,1._rk]
   output_bias = [-.5_rk,.25_rk]
   open(newunit=unit,file='gams-fkb-model.txt',status='replace',action='write',iostat=status)
   if (status /= 0) error stop 'model creation'
   write(unit,'(a)') '5','input 2','dense 3','relu 0','dense 2','linear 0','0.01'
   write(unit,*) hidden_bias
   write(unit,*) output_bias
   write(unit,*) first
   write(unit,*) second
   close(unit,iostat=status)
   if (status /= 0) error stop 'model close'
   call original%load('gams-fkb-model.txt')
   if (original%input_size /= 2 .or. original%output_size /= 2) error stop 'original model dimensions'
   call original%save('gams-fkb-saved.txt')
   call restored%load('gams-fkb-saved.txt')
   if (restored%input_size /= 2 .or. restored%output_size /= 2) error stop 'restored model dimensions'
   cases = 0
   do i = -2,2
      do j = -2,2
         x = real([i,j],rk)
         hidden = hidden_bias
         do k = 1,3
            do l = 1,2
               hidden(k) = hidden(k)+first(l,k)*x(l)
            end do
            hidden(k) = max(0._rk,hidden(k))
         end do
         expected = output_bias
         do k = 1,2
            do l = 1,3
               expected(k) = expected(k)+second(l,k)*hidden(l)
            end do
         end do
         prediction = original%output(x)
         again = restored%output(x)
         if (size(prediction) /= 2 .or. size(again) /= 2) error stop 'prediction dimensions'
         if (.not. all(ieee_is_finite(prediction)) .or. .not. all(ieee_is_finite(again))) &
            error stop 'nonfinite neural prediction'
         if (maxval(abs(prediction-expected)) > 1.e-12_rk) error stop 'independent scalar forward reference'
         if (maxval(abs(again-expected)) > 1.e-12_rk) error stop 'restored scalar forward reference'
         cases = cases+1
         print '(a,2i3,a,2f12.5)', 'Input=',i,j,' outputs=',prediction
      end do
   end do
   if (cases /= 25) error stop 'network input count'
   open(newunit=unit,file='gams-fkb-model.txt',status='old')
   close(unit,status='delete')
   open(newunit=unit,file='gams-fkb-saved.txt',status='old')
   close(unit,status='delete')
   print '(a)', '25 two-output predictions checked against scalar references for original and saved/reloaded networks.'
   print '(a)', 'PASS fkb-network-reference'
end program network_reference
