program demo
  implicit none
  print *, seven()
  contains
  integer function seven() ! preserve this comment
    seven = 7
  end function seven
end program demo
