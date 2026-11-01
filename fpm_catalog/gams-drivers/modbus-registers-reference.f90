! Independent MIT API consumer; see licenses/data-ten-drivers-MIT.txt.
program register_reference
   use, intrinsic :: iso_fortran_env, only: int32
   use modbus, only: c_float,c_uint16_t,modbus_set_float_abcd,modbus_get_float_abcd, &
      modbus_set_float_badc,modbus_get_float_badc,modbus_set_float_cdab,modbus_get_float_cdab, &
      modbus_set_float_dcba,modbus_get_float_dcba
   implicit none
   integer(int32), parameter :: golden(*)=[int(z'00000000',int32),int(z'80000000',int32), &
      int(z'3F800000',int32),int(z'BFA00000',int32),int(z'7F7FFFFF',int32),int(z'00800000',int32), &
      int(z'00000001',int32),int(z'41234567',int32)]
   integer, parameter :: permutation(4,4)=reshape([1,2,3,4,2,1,4,3,3,4,1,2,4,3,2,1],[4,4])
   integer(c_uint16_t) :: words(2),reference(2)
   integer(int32) :: bits,actual_bits
   integer :: fixture,order,j,bytes(4),expected_word,cases
   real(c_float) :: value,actual
   if (storage_size(value)/=32 .or. radix(value)/=2 .or. digits(value)/=24) error stop 'requires binary32'
   cases=0
   do fixture=1,264
      if (fixture<=size(golden)) then
         bits=golden(fixture)
      else
         j=fixture-8
         bits=ior(ishft(modulo(j*11,254),23),iand(j*1234567,int(z'007FFFFF',int32)))
         if (modulo(j,2)==0) bits=ibset(bits,31)
      end if
      value=transfer(bits,value)
      do j=1,4
         bytes(j)=int(iand(shiftr(bits,8*(4-j)),255_int32))
      end do
      do order=1,4
         do j=1,2
            expected_word=256*bytes(permutation(2*j-1,order))+bytes(permutation(2*j,order))
            ! Convert the unsigned register value to its signed Fortran carrier without overflow.
            if (expected_word>=32768) expected_word=expected_word-65536
            reference(j)=int(expected_word,c_uint16_t)
         end do
         select case(order)
         case(1)
            call modbus_set_float_abcd(value,words)
            actual=modbus_get_float_abcd(reference)
         case(2)
            call modbus_set_float_badc(value,words)
            actual=modbus_get_float_badc(reference)
         case(3)
            call modbus_set_float_cdab(value,words)
            actual=modbus_get_float_cdab(reference)
         case(4)
            call modbus_set_float_dcba(value,words)
            actual=modbus_get_float_dcba(reference)
         end select
         if (any(words/=reference)) error stop 'independent register encoding reference'
         actual_bits=transfer(actual,actual_bits)
         if (actual_bits/=bits) error stop 'independent register decoding reference'
         cases=cases+1
      end do
   end do
   if (cases/=1056) error stop 'register fixture count'
   print '(a)', '264 finite binary32 patterns x four byte/word orders: 1056 independent setter and getter checks each.'
   print '(a)', 'Reference register words built from explicit IEEE bits; signed zero, subnormal and extreme finite values.'
   print '(a)', 'Offline conversions only; NaN payloads, infinities, network I/O and physical devices unverified.'
   print '(a)', 'PASS modbus-registers-reference'
end program
