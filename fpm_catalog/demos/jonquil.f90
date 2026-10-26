program main
   use jonquil
   implicit none
   class(json_value), allocatable :: document
   type(json_object), pointer :: object
   type(json_error), allocatable :: error
   integer :: answer
   call json_loads(document, '{"answer":42}', error=error)
   if (allocated(error)) error stop 'JSON parsing failed'
   object => cast_to_object(document)
   call get_value(object,'answer',answer)
   if (answer /= 42) error stop 'incorrect JSON value'
   print *, json_serialize(document)
   print *, 'PASS jonquil'
end program main
