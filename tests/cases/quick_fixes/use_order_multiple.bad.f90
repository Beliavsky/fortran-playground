program demo
  implicit none
  use, intrinsic :: iso_fortran_env, only: int32
  use, intrinsic :: iso_c_binding, only: c_int
  integer(int32) :: n = 7
  integer(c_int) :: m = 8
  print *, n, m
end program demo
