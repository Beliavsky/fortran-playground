module Values
implicit none
contains
integer function answer()
answer = 7
end function answer
end module Values
program main
use Values, only: answer
implicit none
print '(i0)', answer()
end program main
