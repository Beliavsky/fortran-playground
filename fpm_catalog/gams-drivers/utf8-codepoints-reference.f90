! Independent MIT API consumer; see licenses/data-ten-drivers-MIT.txt.
program utf8_reference
   use string_utf_8, only: char_utf,chars_array,chars,substr,indexof,str_replace_all
   implicit none
   integer, parameter :: alphabet(*)=[65,233,8364,119070,769,32]
   type(char_utf), allocatable :: text(:),changed(:)
   character(:), allocatable :: encoded,expected,part,replacement
   integer :: codes(32),n,i,j,k,found,checks,characters
   checks=0; characters=0
   do n=0,32
      encoded=''
      do i=1,n
         codes(i)=alphabet(1+modulo(i*5+n,6)); encoded=encoded//utf8(codes(i))
      end do
      text=chars_array(encoded)
      if (size(text)/=n .or. chars(text)/=encoded) error stop 'UTF-8 code-point round trip'
      checks=checks+1; characters=characters+n
      do i=1,n
         expected=''
         do j=i,min(i+2,n)
            expected=expected//utf8(codes(j))
         end do
         part=chars(substr(text,i,min(3,n-i+1)))
         if (part/=expected) error stop 'UTF-8 positive substring reference'
         checks=checks+1
      end do
      do k=1,size(alphabet)
         found=-1
         do i=1,n
            if (codes(i)/=alphabet(k)) cycle
            found=i; exit
         end do
         if (indexof(text,chars_array(utf8(alphabet(k))))/=found) error stop 'UTF-8 code-point search'
         checks=checks+1
      end do
      do k=1,2
         replacement=''
         if (k==1) replacement=utf8(8364)//'x'
         expected=''
         do i=1,n
            if (codes(i)==233) then
               expected=expected//replacement
            else
               expected=expected//utf8(codes(i))
            end if
         end do
         changed=str_replace_all(text,chars_array(utf8(233)),chars_array(replacement))
         if (chars(changed)/=expected) error stop 'UTF-8 replacement reference'
         checks=checks+1
      end do
   end do
   print '(a,i0,a,i0)', '33 valid UTF-8 fixtures; exact checks: ',checks,'; original code points: ',characters
   print '(a)', 'One/two/three/four-byte code points and combining marks; substrings, single-code-point search and replace/delete.'
   print '(a)', 'Code points, not grapheme clusters; malformed UTF-8, normalization and multi-code-point search unverified.'
   print '(a)', 'PASS utf8-codepoints-reference'
contains
   function utf8(code) result(bytes)
      integer, intent(in) :: code
      character(:), allocatable :: bytes
      if (code<128) then
         bytes=achar(code)
      else if (code<2048) then
         bytes=achar(192+code/64)//achar(128+modulo(code,64))
      else if (code<65536) then
         bytes=achar(224+code/4096)//achar(128+modulo(code/64,64))//achar(128+modulo(code,64))
      else
         bytes=achar(240+code/262144)//achar(128+modulo(code/4096,64))// &
            achar(128+modulo(code/64,64))//achar(128+modulo(code,64))
      end if
   end function
end program
