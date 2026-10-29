module arithmetic_callbacks
   use parser_module, only: parser_t,token_t
   implicit none
contains
   function operand(self,token) result(answer)
      class(parser_t)::self
      type(token_t)::token,answer
      real::value
      integer::status
      read(token%string,*,iostat=status) value
      if(status/=0) error stop 'Invalid numeric operand'
      answer%object=value
   end function operand
   function unary(self,operation,argument) result(answer)
      class(parser_t)::self
      type(token_t)::operation,argument,answer
      select type(value=>argument%object)
      type is(real)
         select case(operation%string)
         case('-');answer%object=-value
         case('+');answer%object=value
         case('sqrt');answer%object=sqrt(value)
         case default;error stop 'Unsupported unary operation'
         end select
      class default
         error stop 'Wrong unary operand type'
      end select
   end function unary
   function binary(self,left,operation,right) result(answer)
      class(parser_t)::self
      type(token_t)::left,operation,right,answer
      select type(a=>left%object)
      type is(real)
         select type(b=>right%object)
         type is(real)
            select case(operation%string)
            case('+');answer%object=a+b
            case('-');answer%object=a-b
            case('*');answer%object=a*b
            case('/');answer%object=a/b
            case('^');answer%object=a**b
            case default;error stop 'Unsupported binary operation'
            end select
         class default
            error stop 'Wrong right operand type'
         end select
      class default
         error stop 'Wrong left operand type'
      end select
   end function binary
end module arithmetic_callbacks

program checked_expressions
   use arithmetic_callbacks
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
   type(parser_t)::parser
   type(token_t)::result
   character(24),parameter::expressions(5)=[character(24):: &
      '2+3*4','(2+3)*4','2^3^2','sqrt(9)','-2+6']
   real,parameter::expected(5)=[14.,20.,512.,3.,4.]
   integer::i
   call parser%register_unary(['-   ','+   '])
   call parser%register_function(['sqrt'])
   call parser%register_operator(['^   '],is_right_assoc=.true.)
   call parser%register_operator(['+   ','-   ','*   ','/   '])
   call parser%ignore_tokens([' '])
   parser%on_operand=>operand
   parser%on_unary=>unary
   parser%on_binary=>binary
   do i=1,size(expressions)
      result=parser%parse(trim(expressions(i)))
      select type(value=>result%object)
      type is(real)
         if(.not.ieee_is_finite(value)) error stop 'Nonfinite expression value'
         if(abs(value-expected(i))>1.e-5) error stop 'Expression mismatch'
         print '(a,a,f10.3)',trim(expressions(i)),' = ',value
      class default
         error stop 'Wrong result type'
      end select
   end do
   print *, 'PASS shunting-yard-fortran'
end program checked_expressions
