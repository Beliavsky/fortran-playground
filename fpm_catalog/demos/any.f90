module demo_values
   use iso_fortran_env, only: int32, real64
   use any_t
   implicit none
contains
   function value(which) result(wrapped)
      integer, intent(in) :: which
      type(any_type) :: wrapped
      select case(which)
      case(1)
         wrapped = 42_int32
      case(2)
         wrapped = 3.125_real64
      case(3)
         wrapped = 'Fortran'
      case default
         error stop 'unknown value'
      end select
   end function
end module

program main
   use demo_values
   implicit none
   integer(int32) :: integer_value
   real(real64) :: real_value
   character(:), allocatable :: text
   integer_value = value(1)
   real_value = value(2)
   text = as_char(value(3))
   if (integer_value /= 42) error stop 'integer retrieval'
   if (abs(real_value-3.125_real64) > 1.0e-14_real64) error stop 'real retrieval'
   if (text /= 'Fortran') error stop 'character retrieval'
   print *, 'Integer:', integer_value
   print *, 'Real:', real_value
   print '(a)', 'Text: '//text
   print *, 'PASS any'
end program
