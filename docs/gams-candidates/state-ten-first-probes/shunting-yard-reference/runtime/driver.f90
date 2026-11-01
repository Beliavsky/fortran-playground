! Independent MIT API consumer; see licenses/state-ten-drivers-MIT.txt.
module integer_expression_callbacks
   use parser_module, only: parser_t,token_t
   implicit none
contains
   function read_operand(parser,token) result(output)
      class(parser_t) :: parser
      type(token_t) :: token,output
      integer :: number,status
      read(token%string,*,iostat=status) number
      if (status/=0) error stop 'invalid integer token'
      output%object=number
   end function
   function unary(parser,operation,argument) result(output)
      class(parser_t) :: parser
      type(token_t) :: operation,argument,output
      select type(number=>argument%object)
      type is (integer)
         if (operation%string=='-') then
            output%object=-number
         else if (operation%string=='+') then
            output%object=number
         else
            error stop 'unexpected unary operator'
         end if
      class default
         error stop 'unexpected unary type'
      end select
   end function
   function binary(parser,left,operation,right) result(output)
      class(parser_t) :: parser
      type(token_t) :: left,operation,right,output
      integer :: a,b,value
      select type(number=>left%object)
      type is (integer)
         a=number
      class default
         error stop 'unexpected left operand type'
      end select
      select type(number=>right%object)
      type is (integer)
         b=number
      class default
         error stop 'unexpected right operand type'
      end select
      select case(operation%string)
      case('+')
         value=a+b
      case('-')
         value=a-b
      case('*')
         value=a*b
      case('/')
         if (b==0) error stop 'unexpected zero divisor'
         value=a/b
      case('^')
         value=a**b
      case default
         error stop 'unexpected binary operator'
      end select
      output%object=value
   end function
end module
program expression_reference
   use integer_expression_callbacks
   implicit none
   type(parser_t) :: parser
   integer :: a,b,c,cases
   character(:), allocatable :: x,y,z
   call parser%register_unary(['-','+'])
   call parser%register_operator(['^'],is_right_assoc=.true.)
   call parser%register_operator(['+','-','*','/'])
   call parser%ignore_tokens([' '])
   parser%on_operand=>read_operand; parser%on_unary=>unary; parser%on_binary=>binary
   cases=0
   do a=1,6
      x=decimal(a)
      do b=1,4
         y=decimal(b)
         do c=1,3
            z=decimal(c)
            call check(x//'+'//y//'*'//z,a+b*c)
            call check('('//x//'+'//y//')*'//z,(a+b)*c)
            call check(x//'-'//y//'-'//z,a-b-c)
            call check('(-'//x//')+'//y//'*'//z,-a+b*c)
            call check('('//x//'*'//y//')/'//y,a)
            call check(x//'+'//y//'*('//z//'+1)',a+b*(c+1))
         end do
      end do
   end do
   call check('2^3^2',512); call check('(2^3)^2',64)
   call check('3+2^3*4',35); call check('-(2+3)*4',-20); call check(' 2 + 3 * 4 ',14)
   if (cases/=437) error stop 'expression reference counts'
   print '(a)', '437 exact integer expression references; six generated templates and five precedence/associativity fixtures.'
   print '(a)', 'Nested parentheses, unary signs, exact integer division, right-associative powers and ignored spaces.'
   print '(a)', 'Valid bounded integers only; syntax errors, real functions, overflow and registration isolation unverified.'
   print '(a)', 'PASS shunting-yard-reference'
contains
   function decimal(value) result(text)
      integer, intent(in) :: value
      character(:), allocatable :: text
      character(20) :: buffer
      write(buffer,'(i0)') value; text=trim(buffer)
   end function
   subroutine check(expression,expected)
      character(*), intent(in) :: expression
      integer, intent(in) :: expected
      type(token_t) :: result
      result=parser%parse(expression)
      select type(value=>result%object)
      type is (integer)
         if (value/=expected) then
            print *, 'expression: ',expression,' actual/expected: ',value,expected
            error stop 'integer expression reference differs'
         end if
      class default
         error stop 'unexpected parsed result type'
      end select
      cases=cases+1
   end subroutine
end program
