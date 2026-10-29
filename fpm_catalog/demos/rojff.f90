program json_round_trip
   use rojff
   implicit none
   type(fallible_json_value_t) :: document, field, restored, invalid
   character(:),allocatable :: serialized
   document=parse_json_from_string('{"steps":12,"dt":0.25,"label":"heat"}')
   if(document%failed()) error stop 'JSON parsing failed'
   select type(object=>document%value_)
   type is(json_object_t)
      field=object%get('steps')
      if(field%failed()) error stop 'Missing steps'
      select type(value=>field%value_)
      type is(json_integer_t)
         if(value%number/=12) error stop 'Wrong integer value'
      type is(json_number_t)
         if(abs(value%number-12.d0)>1.d-12) error stop 'Wrong numeric value'
      class default
         error stop 'steps is not numeric'
      end select
      field=object%get('dt')
      if(field%failed()) error stop 'Missing dt'
      select type(value=>field%value_)
      type is(json_number_t)
         if(abs(value%number-0.25d0)>1.d-12) error stop 'Wrong dt'
      class default
         error stop 'dt is not a number'
      end select
      field=object%get('label')
      if(field%failed()) error stop 'Missing label'
      select type(value=>field%value_)
      type is(json_string_t)
         if(value%string/='heat') error stop 'Wrong label'
      class default
         error stop 'label is not a string'
      end select
      field=object%get('absent')
      if(.not.field%failed()) error stop 'Missing-key error was not reported'
   class default
      error stop 'Expected a JSON object'
   end select
   serialized=document%value_%to_compact_string()
   restored=parse_json_from_string(serialized)
   if(restored%failed()) error stop 'Round-trip parsing failed'
   if(restored%value_%to_compact_string()/=serialized) error stop 'Round trip changed data'
   invalid=parse_json_from_string('{"dt": }')
   if(.not.invalid%failed()) error stop 'Invalid JSON was accepted'
   print '(a)', 'Round-trip JSON: '//serialized
   print '(a)', 'Values, missing-key reporting and malformed-input reporting verified.'
   print *, 'PASS rojff'
end program json_round_trip
