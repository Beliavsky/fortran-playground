program main
implicit none
call show()
contains
subroutine show()
print '(i0)', 7
end subroutine wrong
end program main
