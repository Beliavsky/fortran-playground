program demo_decimal_strings
   use, intrinsic :: iso_fortran_env, only: int64
   use strith, only: strint_type, new_strint, to_string, digits, int64_min, int64_max
   implicit none
   type(strint_type) :: a, b, total, recovered
   character(:), allocatable :: unsigned_value, decimal

   ! Interpret the all-one bit pattern as unsigned, without overflowing int64.
   unsigned_value = to_string(-1_int64, remove_0_padding=.true., as_unsigned=.true.)
   if (unsigned_value /= '18446744073709551615') error stop 'unsigned int64 formatting'
   print '(a)', 'Unsigned 64-bit maximum: '//unsigned_value

   ! The string constructor requires a sign and exactly digits-1 decimal digits.
   a = new_strint('+'//repeat('0', digits - 21)//'18446744073709551615')
   b = new_strint(1_int64)
   total = a + b
   decimal = total%to_string(remove_0_padding=.true.)
   if (decimal /= '18446744073709551616') error stop 'carry beyond 64 bits'
   print '(a)', 'Add one using decimal strings: '//decimal
   recovered = total - b
   if (recovered /= a) error stop 'subtraction round trip'
   a = new_strint(int64_min)
   b = new_strint(int64_max)
   total = a + b
   if (total%to_string(remove_0_padding=.true.) /= '-1') error stop 'opposite signs'
   print '(a)', 'Signed minimum plus signed maximum: -1'
   print '(a)', 'PASS strith'
end program demo_decimal_strings
