module demo
implicit none
interface
  subroutine proc()
  end subroutine wrong
end interface
end module demo
program main
print *, 7
end program main
