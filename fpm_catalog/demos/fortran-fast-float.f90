program main
   use iso_fortran_env, only: int32, int64, real64
   use fast_float_module, only: parse_double, parse_i64, parse_i32, parse_result, &
      parse_options, PRESET_FORTRAN, outcomes
   implicit none
   type(parse_result) :: result
   real(real64) :: value
   integer(int64) :: large
   integer(int32) :: hex

   value = parse_double('3.125e2', res=result)
   if (result%outcome%state /= outcomes%OK%state .or. value /= 312.5_real64) error stop 'decimal'
   print '(a,f8.3)', '3.125e2 = ', value
   value = parse_double('1.25D-2', parse_options(format=PRESET_FORTRAN), res=result)
   if (result%outcome%state /= outcomes%OK%state) error stop 'D exponent status'
   if (abs(value - 0.0125_real64) > 1.0e-16_real64) error stop 'D exponent value'
   print '(a,f8.4)', '1.25D-2 = ', value
   large = parse_i64('9223372036854775807', base=10, res=result)
   if (result%outcome%state /= outcomes%OK%state .or. large /= huge(large)) error stop 'integer limit'
   print '(a,i0)', 'Largest signed 64-bit integer: ', large
   hex = parse_i32('FF', base=16, res=result)
   if (result%outcome%state /= outcomes%OK%state .or. hex /= 255) error stop 'hexadecimal'
   value = parse_double('not-a-number', res=result)
   if (result%outcome%state /= outcomes%INVALID_INPUT%state) error stop 'invalid input'
   print '(a)', 'Invalid input was detected.'
   value = parse_double('1.0e999', res=result)
   if (result%outcome%state /= outcomes%OUT_OF_RANGE%state) error stop 'overflow status'
   print '(a)', 'Out-of-range exponent was detected.'
   print '(a)', 'PASS fortran-fast-float'
end program main
