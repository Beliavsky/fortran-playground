! Adapted from the author's user_object_smart_pointer example.
module demo_resource
   use smart_pointer_m, only: sp_smart_pointer_t
   implicit none
   integer :: cleanup_count = 0
   type, extends(sp_smart_pointer_t) :: resource_t
      integer, pointer :: value => null()
   contains
      procedure :: free
   end type
contains
   impure elemental subroutine free(self)
      class(resource_t), intent(inout) :: self
      if (associated(self%value)) then
         deallocate(self%value)
         nullify(self%value)
         cleanup_count = cleanup_count + 1
      end if
   end subroutine
end module

program main
   use demo_resource
   implicit none
   call exercise()
   if (cleanup_count /= 1) error stop 'cleanup count'
   print *, 'Resource cleaned up exactly once'
   print *, 'PASS smart-pointers'
contains
   subroutine exercise()
      type(resource_t) :: first, second
      allocate(first%value, source=42)
      call first%start_counter()
      if (first%reference_count() /= 1) error stop 'initial count'
      second = first
      if (first%reference_count() /= 2) error stop 'shared count'
      if (.not. associated(first%value, second%value)) error stop 'shared resource'
      if (second%value /= 42) error stop 'resource value'
      print *, 'Shared value:', second%value, 'references:', first%reference_count()
      if (cleanup_count /= 0) error stop 'premature cleanup'
   end subroutine
end program
