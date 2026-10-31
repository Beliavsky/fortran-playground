! Original GAMS A4c API driver. MIT: licenses/arithmetic-drivers-MIT.txt.
program main
   use mpmodule
   implicit none
   integer, parameter :: decimal_digits = 120, words = decimal_digits/mpdpw + 2
   integer :: cases
   type(mp_complex) :: result
   character(*), parameter :: big = '1'//repeat('0',80)
   character(*), parameter :: less_one = repeat('9',80)
   character(*), parameter :: plus_one = '1'//repeat('0',79)//'1'
   character(*), parameter :: plus_two = '1'//repeat('0',79)//'2'
   cases = 0
   ! Component-wise exact decimal references, independent of another complex solver.
   call check(big, '-'//big, '-'//less_one, plus_two, '1', '2')
   print '(a)', '(10^80,-10^80) + (-(10^80-1),10^80+2), recovered components:'
   call mpwrite(6,30,8,mpreal(result,words),aimag(result))
   call check('-'//big, big, less_one, '-'//plus_two, '-1', '-2')
   call check(big, '1', '1', big, plus_one, plus_one)
   call check('0.125', '-0.25', '0.375', '0.75', '0.5', '0.5')
   call check(big, plus_one, '-'//big, '-'//plus_one, '0', '0')
   if (cases /= 5) error stop 'case count'
   print '(a,i0,a,i0)', 'Exact complex sums checked: ', cases, '; requested decimal precision: ', decimal_digits
   print '(a)', 'Checked both components; multiplication and transcendental functions are outside this driver.'
   print '(a)', 'PASS mpfun-complex-addition'
contains
   subroutine check(ar, ai, br, bi, er, ei)
      character(*), intent(in) :: ar, ai, br, bi, er, ei
      type(mp_complex) :: left, right
      type(mp_real) :: expected_real, expected_imag
      left = mpcmplx(number(ar),number(ai),words)
      right = mpcmplx(number(br),number(bi),words)
      expected_real = number(er)
      expected_imag = number(ei)
      result = left + right
      if (mpreal(result,words) /= expected_real .or. aimag(result) /= expected_imag) &
         error stop 'multiprecision complex components'
      cases = cases + 1
   end subroutine
   function number(text) result(value)
      character(*), intent(in) :: text
      type(mp_real) :: value
      ! The author's decimal-string constructor requires a decimal point.
      if (index(text,'.') == 0) then
         value = mpreal(text//'.0',words)
      else
         value = mpreal(text,words)
      end if
   end function
end program
