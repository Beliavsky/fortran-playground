! GNU Fortran 16 rejects this PURE result with a polymorphic allocatable component.
! Compile: gfortran -c pure-result-reproducer.f90
module pure_result_reproducer
   implicit none
   type :: node
      class(*), allocatable :: data
   end type
contains
   type(node) pure function node_init(data)
      class(*), intent(in) :: data
      allocate(node_init%data, source=data)
   end function
end module
