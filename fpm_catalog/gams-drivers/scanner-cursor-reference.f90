! Independent MIT API consumer; see licenses/data-ten-drivers-MIT.txt.
program scanner_reference
   use scanner, only: textscanner
   use stdlib_string_type, only: string_type,assignment(=)
   implicit none
   type(textscanner) :: cursor
   type(string_type) :: input
   character(:), allocatable :: text
   integer :: n,i,j,code,expected,checks
   checks=0
   do n=1,64
      text=repeat(' ',n)
      do i=1,n
         text(i:i)=achar(32+modulo(i*13+n*7,95))
      end do
      input=text; call cursor%new(input)
      do i=1,n
         call check_position(i)
         if (i<n) then
            code=cursor%next()
            if (code/=iachar(text(i+1:i+1))) error stop 'scanner forward reference'
         end if
      end do
      if (cursor%next()/=-1) error stop 'scanner upper boundary'
      call check_position(n)
      do i=n,2,-1
         code=cursor%prev()
         if (code/=iachar(text(i-1:i-1))) error stop 'scanner backward reference'
      end do
      if (cursor%prev()/=-1) error stop 'scanner lower boundary'
      call check_position(1)
      call cursor%skipn(n+5); call check_position(n)
      call cursor%backn(n+5); call check_position(1)
      ! jump_to starts AFTER the current position; missing characters stop at the end.
      do j=32,126,7
         call cursor%first(); expected=n
         do i=2,n
            if (iachar(text(i:i))/=j) cycle
            expected=i; exit
         end do
         call cursor%jump_to(j); call check_position(expected)
      end do
   end do
   print '(a,i0)', '64 nonempty ASCII records; checked cursor positions: ',checks
   print '(a)', 'Exact character oracle; traversal, peek immutability, boundaries, clamped moves and forward jumps.'
   print '(a)', 'Empty input, Unicode character semantics, negative move counts and reverse jumps unverified.'
   print '(a)', 'PASS scanner-cursor-reference'
contains
   subroutine check_position(position)
      integer, intent(in) :: position
      integer :: next_code,previous_code
      if (cursor%current()/=iachar(text(position:position))) error stop 'scanner current reference'
      next_code=-1; previous_code=-1
      if (position<n) next_code=iachar(text(position+1:position+1))
      if (position>1) previous_code=iachar(text(position-1:position-1))
      if (cursor%peek()/=next_code .or. cursor%peek_back()/=previous_code) error stop 'scanner peek reference'
      if (cursor%remaining()/=n-position) error stop 'scanner remaining reference'
      if (cursor%current()/=iachar(text(position:position))) error stop 'scanner peek moved cursor'
      checks=checks+1
   end subroutine
end program
