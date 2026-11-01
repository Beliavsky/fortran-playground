! Independent MIT API consumer; see licenses/data-ten-drivers-MIT.txt.
program enclosure_reference
   use strings_enclose, only: enclose,get_closing_brackets
   implicit none
   character(*), parameter :: alphabet='()[]{}<>x'
   character(8), parameter :: payloads(*)=[character(8) :: '', 'x',' a b ']
   character(:), allocatable :: opening,closing,payload
   integer :: width,code,value,i,j,cases
   cases=0
   do width=0,3
      do code=0,len(alphabet)**width-1
         opening=''; closing=''; value=code
         do i=1,width
            j=1+modulo(value,len(alphabet)); value=value/len(alphabet)
            opening=opening//alphabet(j:j)
            closing=pair(alphabet(j:j))//closing
         end do
         if (get_closing_brackets(opening)/=closing) error stop 'independent closing delimiter map'
         do i=1,size(payloads)
            payload=trim(payloads(i))
            if (enclose(payload,opening)/=opening//payload//closing) error stop 'automatic enclosure'
            if (enclose(payload,opening,autoclose=.false.)/=opening//payload//opening) &
               error stop 'literal repeated enclosure'
            if (enclose(payload,opening,'END')/=opening//payload//'END') error stop 'explicit enclosure'
            cases=cases+1
         end do
      end do
   end do
   if (cases/=2460) error stop 'enclosure fixture count'
   print '(a)', '2460 payload/delimiter fixtures; 820 independently mapped closing strings.'
   print '(a)', 'All combinations through width 3 of paired brackets and an ordinary symbol; empty inputs included.'
   print '(a)', 'Automatic, repeated literal and explicit closing delimiters; UTF-8 delimiter semantics unverified.'
   print '(a)', 'PASS enclose-delimiters-reference'
contains
   character function pair(symbol) result(closing)
      character, intent(in) :: symbol
      select case(symbol)
      case('(')
         closing=')'
      case(')')
         closing='('
      case('[')
         closing=']'
      case(']')
         closing='['
      case('{')
         closing='}'
      case('}')
         closing='{'
      case('<')
         closing='>'
      case('>')
         closing='<'
      case default
         closing=symbol
      end select
   end function
end program
