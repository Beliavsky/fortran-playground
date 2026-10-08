module numbers
  implicit none
  contains
  subroutine work()
    print *, 7
  end subroutine work
end module numbers
program demo
  use numbers
  implicit none
  call work()
end program demo
