program main
implicit none
print '(i0)', answer()
contains
pure integer function answer() result(value)
integer :: i
value = 0
do i = 1, 3
  if (i > 0) then
    value = value + i
  end if
end do
end function answer
end program main
