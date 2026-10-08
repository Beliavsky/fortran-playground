program demo
  implicit none
  call work()
contains
  subroutine work()
    implicit none
    use iso_fortran_env, only: int32
    integer(int32) :: n = 7
    print *, n
  end subroutine work
end program demo
