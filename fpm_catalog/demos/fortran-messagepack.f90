program demo_messagepack
   use messagepack
   use iso_fortran_env, only: int8, int64
   implicit none
   type(msgpack) :: mp
   type(mp_arr_type) :: record
   class(mp_value_type), allocatable :: decoded
   class(mp_arr_type), allocatable :: array
   integer(int8), allocatable :: buffer(:)
   integer(int64) :: number
   character(:), allocatable :: text
   logical :: valid
   ! MessagePack fixarray(2), positive fixint(42), fixstr(7), ASCII 'Fortran'.
   integer, parameter :: expected(*) = [146,42,167,70,111,114,116,114,97,110]

   mp = msgpack()
   record = mp_arr_type(2)
   record%values(1)%obj = mp_int_type(42)
   record%values(2)%obj = mp_str_type('Fortran')
   call mp%pack_alloc(record,buffer)
   if (mp%failed()) error stop 'Packing failed'
   if (size(buffer) /= size(expected)) error stop 'Wrong encoded size'
   if (any(iand(int(buffer),255) /= expected)) error stop 'Unexpected MessagePack bytes'
   call mp%unpack(buffer,decoded)
   if (mp%failed()) error stop 'Unpacking failed'
   call get_arr_ref(decoded,array,valid)
   if (.not. valid) error stop 'Decoded value is not an array'
   if (array%numelements() /= 2) error stop 'Wrong decoded length'
   call get_int(array%values(1)%obj,number,valid)
   if (.not. valid .or. number /= 42_int64) error stop 'Integer differs'
   call get_str(array%values(2)%obj,text,valid)
   if (.not. valid) error stop 'Decoded value is not text'
   if (text /= 'Fortran') error stop 'Text differs'
   print '(a,10(1x,z2.2))', 'MessagePack bytes:',iand(int(buffer),255)
   print '(a,i0,2a)', 'Decoded record: ',number,', ',text
   print '(a)', 'PASS fortran-messagepack'
end program
