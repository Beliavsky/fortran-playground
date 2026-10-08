module numbers
  implicit none
  subroutine work()
    print *, 7
  end subroutine work
end module numbers
program demo
  use numbers
  implicit none
  call work()
end program demo
