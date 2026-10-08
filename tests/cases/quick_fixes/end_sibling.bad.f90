program main
implicit none
call first()
call second()
contains
subroutine first()
print '(i0)', 1
end subroutine first
subroutine second()
print '(i0)', 2
ENDSUBROUTINE first
end program main
