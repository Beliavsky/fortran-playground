! Original GAMS A1 API driver. MIT: licenses/arithmetic-drivers-MIT.txt.
program main
   use iso_fortran_env, only: int64
   use strith, only: strint_type, new_strint, digits
   implicit none
   type(strint_type) :: a, b, result
   integer :: i, j, cases
   character(32) :: expected
   cases = 0
   do i = -20, 20
      do j = -20, 20
         a = new_strint(int(i,int64))
         b = new_strint(int(j,int64))
         result = a + b
         write(expected,'(i0)') i + j
         call check(result, trim(expected))
         result = a - b
         write(expected,'(i0)') i - j
         call check(result, trim(expected))
         cases = cases + 2
      end do
   end do
   ! Exact decimal identities outside int64, without overflowing native integers.
   a = decimal('999999999999999999999999999999')
   b = new_strint(1_int64)
   result = a + b
   call check(result, '1000000000000000000000000000000')
   print '(a)', 'Thirty nines plus one: '//result%to_string(remove_0_padding=.true.)
   a = decimal('1000000000000000000000000000000')
   result = a - b
   call check(result, '999999999999999999999999999999')
   a = decimal('18446744073709551616')
   b = decimal('18446744073709551615')
   result = a - b
   call check(result, '1')
   result = b - a
   call check(result, '-1')
   a = new_strint('-'//repeat('0',digits-31)//'999999999999999999999999999999')
   b = decimal('999999999999999999999999999999')
   result = a + b
   call check(result, '0')
   print '(a,i0,a)', 'Checked ', cases, ' small signed additions/subtractions and 5 large decimal identities.'
   print '(a)', 'Fixed-capacity decimal integers; capacity overflow is outside this example.'
   print '(a)', 'PASS strith-integer-reference'
contains
   function decimal(text) result(value)
      character(*), intent(in) :: text
      type(strint_type) :: value
      if (len(text) >= digits) error stop 'decimal capacity'
      value = new_strint('+'//repeat('0',digits-1-len(text))//text)
   end function
   subroutine check(value, text)
      type(strint_type), intent(in) :: value
      character(*), intent(in) :: text
      character(:), allocatable :: actual
      actual = value%to_string(remove_0_padding=.true.)
      if (actual /= text) then
         print '(a)', 'Expected '//text//'; got '//actual
         error stop 'decimal integer check'
      end if
   end subroutine
end program
