! Independent MIT consumer; see licenses/storage-ten-drivers-MIT.txt.
module checked_resource
   use smart_pointer_m, only: sp_smart_pointer_t
   implicit none
   integer :: cleaned=0,checksum=0
   type,extends(sp_smart_pointer_t) :: resource
      integer,pointer :: data(:)=>null()
   contains
      procedure :: free
   end type
contains
   impure elemental subroutine free(self)
      class(resource),intent(inout) :: self
      if(associated(self%data)) then
         checksum=checksum+sum(self%data)
         cleaned=cleaned+1
         deallocate(self%data)
         nullify(self%data)
      end if
   end subroutine
end module
program main
   use checked_resource
   implicit none
   integer :: n,expected
   expected=0
   do n=1,64
      call fixture(n)
      expected=expected+n*n*(n+1)/2
      if(cleaned/=n .or. checksum/=expected) error stop 'Exactly-once resource cleanup'
   end do
   print '(a)', '64 owned-array lifetimes; nested aliases, shared mutation and exactly-once cleanup'
   print '(a)', 'PASS smart-lifetime-reference'
contains
   subroutine fixture(n)
      integer,intent(in) :: n
      type(resource) :: owner
      integer :: i
      allocate(owner%data(n))
      owner%data=[(i,i=1,n)]
      call owner%start_counter()
      if(owner%reference_count()/=1) error stop 'Owner count'
      call alias_scope(owner,n)
      if(owner%reference_count()/=1) error stop 'Alias release'
      if(any(owner%data/=[(n*i,i=1,n)])) error stop 'Shared mutations'
      if(cleaned/=n-1) error stop 'Premature cleanup'
   end subroutine
   subroutine alias_scope(owner,n)
      type(resource),intent(in) :: owner
      integer,intent(in) :: n
      type(resource) :: alias
      alias=owner
      if(owner%reference_count()/=2) error stop 'Two aliases'
      if(.not.associated(owner%data,alias%data)) error stop 'Shared target'
      call third_scope(alias,n)
      if(owner%reference_count()/=2) error stop 'Third alias release'
   end subroutine
   subroutine third_scope(owner,n)
      type(resource),intent(in) :: owner
      integer,intent(in) :: n
      type(resource) :: alias
      alias=owner
      if(owner%reference_count()/=3) error stop 'Three aliases'
      alias%data=alias%data*n
   end subroutine
end program
