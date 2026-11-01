! Independent MIT API consumer; see licenses/data-ten-drivers-MIT.txt.
module reference_field_rules
   implicit none
contains
   logical function valid(token)
      character(*), intent(in) :: token
      valid=scan(token,' ,;'//achar(9)//achar(10))==0
   end function
   logical function ignored(token)
      character(*), intent(in) :: token
      ignored=.false.
      if (len(token)>0) ignored=token(1:1)=='!'
   end function
end module
program tokenizer_reference
   use fortran_tokenizer, only: tokenizer_t,token_t,token_list,list_size=>size
   use reference_field_rules
   implicit none
   type(tokenizer_t) :: tokenizer
   type(token_list) :: tokens
   type(token_t) :: token
   character(:), allocatable :: input
   character(16) :: word,expected(17)
   character(1), parameter :: separators(*)=[' ',',',';',achar(9),achar(10)]
   integer :: fixture,k,n,i,counted,fields
   fields=0
   do fixture=1,64
      input=' ,'; counted=0; n=1+modulo(fixture,17)
      do k=1,n
         write(word,'(a,i0,a,i0)') 'f',fixture,'_',k
         if (modulo(k+fixture,4)==0) then
            word='!'//trim(word)
         else
            counted=counted+1; expected(counted)=word
         end if
         input=input//trim(word)//repeat(separators(1+modulo(k+fixture,5)),1+modulo(k,3))
      end do
      if (modulo(fixture,2)==0) then
         tokenizer%validator=>valid; tokenizer%ignore=>ignored
         tokens=tokenizer%tokenize(input)
      else
         nullify(tokenizer%validator,tokenizer%ignore)
         tokens=tokenizer%tokenize(input,validate=valid,ignore=ignored)
      end if
      if (list_size(tokens)/=counted) error stop 'token field count reference'
      do i=1,counted
         token=tokens%get(i)
         if (token%string/=trim(expected(i))) error stop 'token field content reference'
      end do
      fields=fields+counted
      call tokens%clear()
      if (list_size(tokens)/=0) error stop 'token list clear'
   end do
   tokens=tokenizer%tokenize('',validate=valid,ignore=ignored)
   if (list_size(tokens)/=0) error stop 'empty token stream'
   call tokens%clear()
   print '(a,i0)', '64 generated records plus empty input; exact retained field references: ',fields
   print '(a)', 'Five delimiters, repeated/leading/trailing separators, ignore rules and stored/argument callbacks.'
   print '(a)', 'Custom delimiter rules only; quoting, escaping, Unicode lexical rules and default validator unverified.'
   print '(a)', 'PASS tokenizer-fields-reference'
end program
