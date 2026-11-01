! Independent MIT consumer; see licenses/interop-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64
   use rojff
   implicit none
   type(fallible_json_value_t) :: document, restored, invalid
   character(200) :: source
   integer :: i
   do i = -24, 24
      write(source,'(a,i0,a,f10.3,a,i0,a)') '{"count":', i, ',"dt":', real(i,real64)/8, &
         ',"label":"case', i, '"}'
      document = parse_json_from_string(trim(source))
      call verify(document,i)
      restored = parse_json_from_string(document%value_%to_compact_string())
      call verify(restored,i)
   end do
   invalid = parse_json_from_string('{"count": }')
   if (.not. invalid%failed()) error stop 'Accepted missing value'
   invalid = parse_json_from_string('{"count":1')
   if (.not. invalid%failed()) error stop 'Accepted unclosed object'
   print '(a)', '49 objects; 294 independent typed references; two malformed inputs rejected'
   print '(a)', 'PASS rojff-json-reference'
contains
   subroutine verify(doc,n)
      type(fallible_json_value_t), intent(in) :: doc
      integer, intent(in) :: n
      type(fallible_json_value_t) :: field
      character(20) :: label
      if (doc%failed()) error stop 'JSON parse failed'
      write(label,'(a,i0)') 'case',n
      select type(obj => doc%value_)
      type is(json_object_t)
         field = obj%get('count')
         if (field%failed()) error stop 'Missing count'
         select type(value => field%value_)
         type is(json_integer_t)
            if (value%number /= n) error stop 'Integer mismatch'
         class default
            error stop 'Integer type mismatch'
         end select
         field = obj%get('dt')
         if (field%failed()) error stop 'Missing dt'
         select type(value => field%value_)
         type is(json_number_t)
            if (value%number /= real(n,real64)/8) error stop 'Real mismatch'
         class default
            error stop 'Real type mismatch'
         end select
         field = obj%get('label')
         if (field%failed()) error stop 'Missing label'
         select type(value => field%value_)
         type is(json_string_t)
            if (value%string /= trim(label)) error stop 'String mismatch'
         class default
            error stop 'String type mismatch'
         end select
         field = obj%get('absent')
         if (.not. field%failed()) error stop 'Absent key found'
      class default
         error stop 'Object type mismatch'
      end select
   end subroutine
end program
