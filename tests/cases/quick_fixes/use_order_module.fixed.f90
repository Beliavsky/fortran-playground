module numbers
  use iso_fortran_env, only: int32
  implicit none
  integer(int32), parameter :: n = 7
end module numbers
program demo
  use numbers
  implicit none
  print *, n
end program demo
