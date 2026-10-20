! Example: Basics: arithmetic and formatted output
! Try changing a and b; compare integer and real division.
program arithmetic
   implicit none
   integer :: a = 7, b = 2
   print '(a,i0)', 'Integer division: ', a/b
   print '(a,f6.2)', 'Real division: ', real(a)/real(b)
   print '(a,i0)', 'Remainder: ', mod(a,b)
end program arithmetic
