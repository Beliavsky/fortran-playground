! Independent API consumer; MIT: licenses/data-kinds-drivers-MIT.txt.
program parsing_reference
   use fast_float_module, only: parse_double, parse_i64, parse_i32, parse_result, &
      parse_options, PRESET_FORTRAN, outcomes
   use, intrinsic :: iso_fortran_env, only: int32,int64,real64
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer(int64), parameter :: integers(*) = [-huge(0_int64)-1_int64,-huge(0_int64), &
      -100000_int64,-1_int64,0_int64,1_int64,255_int64,huge(0_int64)]
   integer(int32), parameter :: small(*) = [-huge(0_int32)-1_int32,-100000_int32, &
      -1_int32,0_int32,1_int32,255_int32,huge(0_int32)]
   type(parse_result) :: status
   real(real64) :: value,expected
   integer(int64) :: large
   integer(int32) :: number
   character(40) :: text
   integer :: i,calls
   calls = 0
   do i = -64,64
      expected = real(i,real64)/8
      write(text,'(f12.3)') expected
      value = parse_double(trim(adjustl(text)),res=status)
      call ok()
      if (.not. ieee_is_finite(value) .or. value /= expected) error stop 'exact dyadic decimal'
   end do
   do i = 1,size(integers)
      write(text,'(i0)') integers(i)
      large = parse_i64(trim(text),base=10,res=status)
      call ok()
      if (large /= integers(i)) error stop 'signed int64 decimal reference'
   end do
   do i = 1,size(small)
      write(text,'(i0)') small(i)
      number = parse_i32(trim(text),base=10,res=status)
      call ok()
      if (number /= small(i)) error stop 'signed int32 decimal reference'
   end do
   large = parse_i64('11111111',base=2,res=status)
   call ok()
   if (large /= 255_int64) error stop 'binary integer'
   number = parse_i32('7FFFFFFF',base=16,res=status)
   call ok()
   if (number /= huge(0_int32)) error stop 'hex integer'
   value = parse_double('1.25D-1',parse_options(format=PRESET_FORTRAN),res=status)
   call ok()
   if (value /= .125_real64) error stop 'Fortran D exponent'
   value = parse_double('9007199254740993',res=status)
   call ok()
   if (value /= 9007199254740992._real64) error stop 'binary64 halfway rounding'
   value = parse_double('not-a-number',res=status)
   if (status%outcome%state /= outcomes%INVALID_INPUT%state) error stop 'invalid float status'
   large = parse_i64('not-an-integer',base=10,res=status)
   if (status%outcome%state /= outcomes%INVALID_INPUT%state) error stop 'invalid integer status'
   value = parse_double('1e999',res=status)
   if (status%outcome%state /= outcomes%OUT_OF_RANGE%state) error stop 'float overflow status'
   large = parse_i64('9223372036854775808',base=10,res=status)
   if (status%outcome%state /= outcomes%OUT_OF_RANGE%state) error stop 'int64 positive overflow status'
   large = parse_i64('-9223372036854775809',base=10,res=status)
   if (status%outcome%state /= outcomes%OUT_OF_RANGE%state) error stop 'int64 negative overflow status'
   number = parse_i32('2147483648',base=10,res=status)
   if (status%outcome%state /= outcomes%OUT_OF_RANGE%state) error stop 'int32 overflow status'
   if (calls /= 148) error stop 'successful parse count'
   print '(a)', '129 exact binary-fraction decimals and 15 signed decimal integers checked.'
   print '(a)', 'Binary/hex integers, D exponent and a binary64 halfway case checked.'
   print '(a)', 'Six invalid/overflow outcomes checked; 154 parser calls in total.'
   print '(a)', 'PASS fast-float-parsing-reference'
contains
   subroutine ok()
      if (status%outcome%state /= outcomes%OK%state) error stop 'valid parse status'
      calls = calls+1
   end subroutine ok
end program parsing_reference
