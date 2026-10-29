module integer_list_order
   use common_mod, only: DATA_KIND
   implicit none
contains
   integer function compare_values(a, b) result(order)
      integer(DATA_KIND), intent(in) :: a(:), b(:)
      order = 0
      if (a(1) < b(1)) order = -1
      if (a(1) > b(1)) order = 1
   end function compare_values
end module integer_list_order

program demo_linked_list
   use common_mod, only: DATA_KIND
   use dll_mod, only: dll_t
   use dllnode_mod, only: dllnode_t, dllnode_read
   use integer_list_order, only: compare_values
   implicit none
   type(dll_t) :: values
   type(dllnode_t), pointer :: node
   integer(DATA_KIND), parameter :: input(*) = [4_DATA_KIND, 1_DATA_KIND, 3_DATA_KIND, 2_DATA_KIND, 3_DATA_KIND]
   integer(DATA_KIND), parameter :: expected(*) = [1_DATA_KIND, 2_DATA_KIND, 3_DATA_KIND, 3_DATA_KIND, 4_DATA_KIND]
   integer(DATA_KIND), allocatable :: item(:)
   integer :: i

   do i = 1, size(input)
      call values%append([input(i)])
   end do
   if (values%count([3_DATA_KIND]) /= 2) error stop 'duplicate count'
   call values%sort(compare_values)
   node => values%firstnode()
   print '(a)', 'Sorted linked list:'
   do i = 1, size(expected)
      if (.not. associated(node)) error stop 'list too short'
      item = dllnode_read(node)
      if (size(item) /= 1) error stop 'node shape'
      if (item(1) /= expected(i)) error stop 'sort order'
      print '(i4)', item(1)
      node => node%nextnode()
   end do
   if (associated(node)) error stop 'list too long'
   node => values%index([2_DATA_KIND])
   if (.not. associated(node)) error stop 'search'
   call values%remove([2_DATA_KIND])
   if (values%count([2_DATA_KIND]) /= 0) error stop 'remove'
   if (values%count([3_DATA_KIND]) /= 2) error stop 'other entries changed'
   call values%clear()
   if (associated(values%firstnode())) error stop 'clear'
   print '(a)', 'PASS list'
end program demo_linked_list
