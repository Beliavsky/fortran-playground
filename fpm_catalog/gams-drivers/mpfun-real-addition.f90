! Original GAMS A3c API driver. MIT: licenses/arithmetic-drivers-MIT.txt.
program main
   use mpmodule
   implicit none
   integer, parameter :: decimal_digits = 120, words = decimal_digits/mpdpw + 2
   integer :: cases
   type(mp_real) :: result
   character(*), parameter :: huge_integer = '1'//repeat('0',80)
   character(*), parameter :: huge_plus_one = '1'//repeat('0',79)//'1'
   cases = 0
   call check(huge_integer, '1', huge_plus_one)
   call check('1', huge_integer, huge_plus_one)
   call check('-'//huge_integer, '-1', '-'//huge_plus_one)
   call check(huge_integer, '-'//huge_integer, '0')
   call check('123456789012345678901234567890', '987654321098765432109876543210', &
      '1111111110111111111011111111100')
   call check('0.125', '0.375', '0.5')
   if (cases /= 6) error stop 'case count'
   print '(a)', 'Exact decimal identity: 10^80 + 1 = 1 followed by 79 zeroes and 1.'
   print '(a)', 'Also checked operand order, negative addition, cancellation and an explicit 31-digit sum.'
   print '(a)', 'Computed dyadic sum 0.125 + 0.375:'
   call mpwrite(6,30,8,result)
   print '(a,i0,a,i0)', 'Checked additions: ', cases, '; requested decimal precision: ', decimal_digits
   print '(a)', 'PASS mpfun-real-addition'
contains
   subroutine check(left_text, right_text, expected_text)
      character(*), intent(in) :: left_text, right_text, expected_text
      type(mp_real) :: left, right, expected
      left = number(left_text)
      right = number(right_text)
      expected = number(expected_text)
      result = left + right
      if (result /= expected) then
         print '(a)', left_text//' + '//right_text//' /= '//expected_text
         error stop 'multiprecision real addition'
      end if
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
