program main
   use strings_enclose, only: enclose, get_closing_brackets
   implicit none
   character(:), allocatable :: nested

   nested = enclose('x', '([{')
   if (nested /= '([{x}])') error stop 'nested brackets'
   if (get_closing_brackets('([{') /= '}])') error stop 'closing brackets'
   if (enclose('value', '[') /= '[value]') error stop 'square brackets'
   if (enclose('name', '"') /= '"name"') error stop 'quotes'
   if (enclose('text', '<<', '>>') /= '<<text>>') error stop 'explicit delimiters'
   if (enclose('x', 'ab', autoclose=.false.) /= 'abxab') error stop 'same delimiters'
   print '(a)', nested
   print '(a)', enclose('value', '[')
   print '(a)', enclose('name', '"')
   print '(a)', enclose('text', '<<', '>>')
   print '(a)', 'PASS enclose'
end program main
