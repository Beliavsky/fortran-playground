program register_conversions
   ! Offline libmodbus operations: no connection or physical device is needed.
   use modbus, only: c_float, c_uint16_t, modbus_set_float_abcd, modbus_get_float_abcd, &
      modbus_set_float_badc, modbus_get_float_badc, modbus_set_float_cdab, &
      modbus_get_float_cdab, modbus_set_float_dcba, modbus_get_float_dcba
   implicit none
   integer(c_uint16_t) :: registers(2)
   real(c_float), parameter :: values(4) = &
      [12.5_c_float, -3.25_c_float, 0.0_c_float, 123.456_c_float]
   real(c_float) :: restored
   integer :: i

   print '(a)', '32-bit floating-point values stored in two 16-bit registers:'
   do i = 1, size(values)
      call modbus_set_float_abcd(values(i), registers)
      restored = modbus_get_float_abcd(registers)
      call check('ABCD', values(i), restored, registers)
      call modbus_set_float_badc(values(i), registers)
      restored = modbus_get_float_badc(registers)
      call check('BADC', values(i), restored, registers)
      call modbus_set_float_cdab(values(i), registers)
      restored = modbus_get_float_cdab(registers)
      call check('CDAB', values(i), restored, registers)
      call modbus_set_float_dcba(values(i), registers)
      restored = modbus_get_float_dcba(registers)
      call check('DCBA', values(i), restored, registers)
   end do
   print '(a)', 'PASS fortran-modbus'
contains
   subroutine check(order, original, actual, words)
      character(len=*), intent(in) :: order
      real(c_float), intent(in) :: original, actual
      integer(c_uint16_t), intent(in) :: words(2)
      if (actual /= original) error stop 'register conversion round trip'
      print '(a,1x,f8.3,2(1x,z4.4),a,f8.3)', order, original, words, ' -> ', actual
   end subroutine check
end program register_conversions
