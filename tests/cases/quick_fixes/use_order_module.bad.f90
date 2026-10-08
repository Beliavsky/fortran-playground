module numbers
  implicit none
  use iso_fortran_env, only: int32
  integer(int32), parameter :: n = 7
end module numbers
program demo
  use numbers
  implicit none
  print *, n
end program demo
