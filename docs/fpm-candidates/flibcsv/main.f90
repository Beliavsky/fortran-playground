module csv_demo_callbacks
   use iso_c_binding
   implicit none
   integer :: field_count = 0, row_count = 0
   character(16) :: fields(3)
contains
   subroutine field(data, length, context) bind(C)
      type(c_ptr), value :: data, context
      integer(c_size_t), value :: length
      character(c_char), pointer :: chars(:)
      integer :: i
      field_count = field_count+1
      if (field_count > 3 .or. length > 16) error stop 'unexpected CSV field'
      fields(field_count) = ' '
      if (length == 0) return
      call c_f_pointer(data, chars, [int(length)])
      do i = 1, int(length)
         fields(field_count)(i:i) = chars(i)
      end do
   end subroutine
   subroutine row(terminator, context) bind(C)
      integer(c_int), value :: terminator
      type(c_ptr), value :: context
      row_count = row_count+1
   end subroutine
end module

program main
   use csv_demo_callbacks
   use flibcsv
   implicit none
   type(csv_parser) :: parser
   character(*), parameter :: input = '"red,green",,"say ""hi"""'//achar(10)
   integer(c_size_t) :: consumed
   integer(c_int) :: status
   status = csv_init(parser, int(CSV_STRICT,c_signed_char))
   if (status /= 0) error stop 'CSV init'
   consumed = csv_parse(parser, input, int(len(input),c_size_t), &
      c_funloc(field), c_funloc(row), c_null_ptr)
   if (consumed /= len(input)) error stop 'CSV parse'
   status = csv_fini(parser, c_funloc(field), c_funloc(row), c_null_ptr)
   if (status /= 0) error stop 'CSV finalization'
   call csv_free(parser)
   if (field_count /= 3 .or. row_count /= 1) error stop 'CSV counts'
   if (any(fields /= [character(16) :: 'red,green','','say "hi"'])) error stop 'CSV contents'
   print '(a)', 'Quoted field: '//trim(fields(1)), 'Empty field checked', trim(fields(3))
   print *, 'PASS flibcsv'
end program
