module demo_token_rules
   implicit none
contains
   logical function field(token)
      character(*), intent(in) :: token
      field = scan(token, ' ,' // achar(9)) == 0
   end function
end module

program main
   use fortran_tokenizer, only: tokenizer_t, token_list, token_t, size
   use demo_token_rules, only: field
   implicit none
   type(tokenizer_t) :: tokenizer
   type(token_list) :: tokens
   type(token_t) :: token
   character(5), parameter :: expected(3) = ['alpha', 'beta ', 'gamma']
   integer :: i
   tokens = tokenizer%tokenize('alpha, beta' // achar(9) // ',gamma', validate=field)
   if (size(tokens) /= 3) error stop 'token count'
   do i = 1, 3
      token = tokens%get(i)
      if (token%string /= trim(expected(i))) error stop 'token contents'
      print '(i0,2a)', i, ': ', token%string
   end do
   call tokens%clear()
   if (size(tokens) /= 0) error stop 'clear'
   print *, 'PASS fortran-tokenizer'
end program
