! Independent MIT consumer; see licenses/storage-ten-drivers-MIT.txt.
program main
   use regex, only: re_match
   implicit none
   character(4),parameter :: alphabet='01a.'
   character(4) :: text
   integer :: n,k,j,q,point,count
   logical :: decimal,identifier
   count=0
   do n=1,4
      do k=0,4**n-1
         q=k
         do j=1,n
            text(j:j)=alphabet(mod(q,4)+1:mod(q,4)+1)
            q=q/4
         end do
         ! A direct character-state grammar, independent of regex machinery.
         point=0
         decimal=.true.
         do j=1,n
            if(text(j:j)=='.') then
               if(point/=0) decimal=.false.
               point=j
            else if(index('01',text(j:j))==0) then
               decimal=.false.
            end if
         end do
         decimal=decimal.and.point>1.and.point<n
         identifier=text(1:1)=='a'
         do j=2,n
            if(index('01a',text(j:j))==0) identifier=.false.
         end do
         if(re_match('^\d+\.\d+$',text(:n)).neqv.decimal) error stop 'Decimal grammar'
         if(re_match('^a[01a]*$',text(:n)).neqv.identifier) error stop 'Identifier grammar'
         count=count+2
      end do
   end do
   print '(a,i0)', '340 exhaustive strings; independent decimal/identifier grammar comparisons: ',count
   print '(a)', 'PASS regex-language-reference'
end program
