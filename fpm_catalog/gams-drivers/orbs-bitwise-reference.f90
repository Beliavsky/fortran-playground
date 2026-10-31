! Independent API consumer; see licenses/unsigned-bitsets-drivers-MIT.txt.
program checked_bitsets
   use orbs
   implicit none
   integer, parameter :: widths(11)=[1,4,8,31,32,63,64,65,127,128,129]
   type(operable_bitset) :: a,b,c
   character(:), allocatable :: lhs,rhs,expected
   integer :: w,n,i,j,k,amount,carry,digit,borrow,checks=0,pairs=0
   do w=1,size(widths)
      n=widths(w)
      do i=0,15
         lhs=pattern(n,i); a=operable_bitset(lhs)
         do j=0,15
            rhs=pattern(n,j); b=operable_bitset(rhs)
            expected=repeat('0',n)
            do k=1,n
               if (lhs(k:k)=='1'.and.rhs(k:k)=='1') expected(k:k)='1'
            end do
            c=a.and.b; call compare(c,expected)
            do k=1,n
               expected(k:k)='0'
               if (lhs(k:k)=='1'.or.rhs(k:k)=='1') expected(k:k)='1'
            end do
            c=a.or.b; call compare(c,expected)
            do k=1,n
               expected(k:k)='0'
               if (lhs(k:k)/=rhs(k:k)) expected(k:k)='1'
            end do
            c=a.xor.b; call compare(c,expected)
            do k=1,n
               expected(k:k)='0'
               if (lhs(k:k)=='1'.and.rhs(k:k)=='0') expected(k:k)='1'
            end do
            c=a.andnot.b; call compare(c,expected)
            ! Schoolbook base-two arithmetic, independent of bitset and bstrith calls.
            carry=0
            do k=n,1,-1
               digit=merge(1,0,lhs(k:k)=='1')+merge(1,0,rhs(k:k)=='1')+carry
               expected(k:k)=achar(iachar('0')+modulo(digit,2)); carry=digit/2
            end do
            c=a+b; call compare(c,expected)
            borrow=0
            do k=n,1,-1
               digit=merge(1,0,lhs(k:k)=='1')-merge(1,0,rhs(k:k)=='1')-borrow
               expected(k:k)=achar(iachar('0')+modulo(digit,2)); borrow=merge(1,0,digit<0)
            end do
            c=a-b; call compare(c,expected)
            if (a%to_string()/=lhs.or.b%to_string()/=rhs) error stop 'bitset operands changed'
            pairs=pairs+1
         end do
         expected=lhs
         do k=1,n
            expected(k:k)=merge('0','1',lhs(k:k)=='1')
         end do
         c=.not.a; call compare(c,expected)
         ! Stay strictly inside the documented shift domain, including zero.
         do amount=1-n,n-1
            expected=repeat('0',n)
            do k=1,n
               if (k+amount<1.or.k+amount>n) cycle
               expected(k:k)=lhs(k+amount:k+amount)
            end do
            c=a.shift.amount; call compare(c,expected)
         end do
      end do
   end do
   print '(a,i0)', 'Bitset widths: ',size(widths)
   print '(a,i0)', 'Operand pairs: ',pairs
   print '(a,i0)', 'Exact binary-string references: ',checks
   print '(a)', 'PASS orbs-bitwise-reference'
contains
   function pattern(n,seed) result(text)
      integer, intent(in) :: n,seed
      character(n) :: text
      integer :: k
      text=repeat('0',n)
      select case(seed)
      case(0)
      case(1)
         text=repeat('1',n)
      case(2)
         text(n:n)='1'
      case(3)
         text(1:1)='1'
      case default
         do k=1,n
            if (modulo(k*k+seed*k+seed*seed,17)<8) text(k:k)='1'
         end do
      end select
   end function pattern
   subroutine compare(value,reference)
      type(operable_bitset), intent(in) :: value
      character(*), intent(in) :: reference
      if (value%bits()/=len(reference)) error stop 'bitset width changed'
      if (value%to_string()/=reference) error stop 'independent binary reference mismatch'
      checks=checks+1
   end subroutine compare
end program checked_bitsets
