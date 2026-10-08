module numbers
  implicit none
  contains
  integer function seven() result(n)
    n = 7
  end function seven
end module numbers
program demo
  use numbers
  implicit none
  print *, seven()
end program demo
