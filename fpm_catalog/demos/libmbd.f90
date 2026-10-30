! Argon dimer energy and forces, adapted from the author's mbd_api_tests.F90.
program main
   use mbd, only: mbd_input_t, mbd_calc_t
   use mbd_constants, only: dp, ang, MBD_LOG_LVL_ERROR
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   type(mbd_input_t) :: input
   type(mbd_calc_t) :: calculation
   real(dp) :: energy, gradients(3,2)
   integer :: code
   character(200) :: origin, message
   input%atom_types = ['Ar', 'Ar']
   input%coords = reshape([0.0_dp, 0.0_dp, 0.0_dp, 0.0_dp, 0.0_dp, 4.0_dp*ang], [3,2])
   input%xc = 'pbe'
   input%log_level = MBD_LOG_LVL_ERROR
   call calculation%init(input)
   call check_exception()
   call calculation%update_vdw_params_custom([11.0_dp,11.0_dp], [63.525_dp,63.525_dp], [3.55_dp,3.55_dp])
   call check_exception()
   call calculation%evaluate_vdw_method(energy)
   call check_exception()
   call calculation%get_gradients(gradients)
   call check_exception()
   call calculation%destroy()
   if (.not. ieee_is_finite(energy) .or. .not. all(ieee_is_finite(gradients))) error stop 'Nonfinite result'
   if (abs(energy-(-2.4329456747018696e-4_dp)) > 1.0e-13_dp) error stop 'Energy differs from reference'
   if (abs(sum(abs(gradients))-2.3279742219399908e-4_dp) > 1.0e-13_dp) error stop 'Wrong gradients'
   if (maxval(abs(sum(gradients,dim=2))) > 1.0e-13_dp) error stop 'Forces are not equal and opposite'
   print '(a,es20.12)', 'Argon dimer dispersion energy (hartree): ', energy
   print '(a,es20.12)', 'Sum of absolute gradients: ', sum(abs(gradients))
   print '(a)', 'PASS libmbd'
contains
   subroutine check_exception()
      call calculation%get_exception(code, origin, message)
      if (code /= 0) then
         print '(a)', trim(origin)//': '//trim(message)
         error stop 'libMBD reported an exception'
      end if
   end subroutine check_exception
end program main
