program main
   use iso_varying_string, only: var_str,char
   use parff, only: parser_output_t,parsed_integer_t,new_state,parse_integer
   implicit none
   type(parser_output_t) :: result
   result=parse_integer(new_state(var_str('-321')))
   if (.not.result%ok) error stop 'Valid integer was rejected'
   select type (value=>result%parsed)
   type is (parsed_integer_t)
      if (value%value_/=-321) error stop 'Incorrect parsed value'
      print '(a,i0)', 'Parsed integer: ',value%value_
   class default
      error stop 'Unexpected result type'
   end select
   result=parse_integer(new_state(var_str('not a number')))
   if (result%ok) error stop 'Invalid integer was accepted'
   print '(a,a)', 'Invalid input: ',char(result%message%to_string())
   print *, 'PASS parff'
end program
