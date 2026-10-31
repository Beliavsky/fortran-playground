! Independent API consumer; MIT: licenses/data-kinds-drivers-MIT.txt.
program machine_reference
   use penf, only: penf_init,is_initialized,endian,endianL,endianB,I1P,I2P,I4P,I8P,R4P,R8P, &
      BII1P,BII2P,BII4P,BII8P,BIR4P,BIR8P,BYI1P,BYI2P,BYI4P,BYI8P,BYR4P,BYR8P, &
      MaxI1P,MaxI2P,MaxI4P,MaxI8P,MaxR4P,MaxR8P,smallR4P,smallR8P,byte_size
   use, intrinsic :: iso_fortran_env, only: int8,int16,int32,int64,real32,real64
   implicit none
   real(R4P), volatile :: step4,one4,next4
   real(R8P), volatile :: step8,one8,next8
   integer(int8) :: bytes(4)
   integer :: count4,count8,order
   call penf_init()
   if (.not. is_initialized) error stop 'PENF initialization state'
   if (any([I1P,I2P,I4P,I8P] /= [int8,int16,int32,int64])) error stop 'ISO integer kinds'
   if (any([R4P,R8P] /= [real32,real64])) error stop 'ISO real kinds'
   if (any([int(BII1P),int(BII2P),int(BII4P),int(BII8P)] /= [8,16,32,64])) error stop 'integer storage bits'
   if (any([int(BIR4P),int(BIR8P)] /= [storage_size(0._real32),storage_size(0._real64)])) &
      error stop 'real storage bits'
   if (any([int(BYI1P),int(BYI2P),int(BYI4P),int(BYI8P)] /= [1,2,4,8])) error stop 'integer bytes'
   if (any([int(BYR4P),int(BYR8P)] /= [4,8])) error stop 'real bytes'
   if (byte_size(0_I1P) /= 1 .or. byte_size(0_I2P) /= 2) error stop 'small integer byte inquiry'
   if (byte_size(0_I4P) /= 4 .or. byte_size(0_I8P) /= 8) error stop 'large integer byte inquiry'
   if (byte_size(0._R4P) /= 4 .or. byte_size(0._R8P) /= 8) error stop 'real byte inquiry'
   if (MaxI1P /= huge(0_int8) .or. MaxI2P /= huge(0_int16)) error stop 'small integer maxima'
   if (MaxI4P /= huge(0_int32) .or. MaxI8P /= huge(0_int64)) error stop 'large integer maxima'
   if (MaxR4P /= huge(0._real32) .or. MaxR8P /= huge(0._real64)) error stop 'real maxima'
   if (smallR4P /= tiny(0._real32) .or. smallR8P /= tiny(0._real64)) error stop 'normal real minima'
   bytes = transfer(int(z'01020304',int32),bytes)
   if (all(bytes == [4_int8,3_int8,2_int8,1_int8])) then
      order = endianL
   else if (all(bytes == [1_int8,2_int8,3_int8,4_int8])) then
      order = endianB
   else
      error stop 'unsupported mixed byte order'
   end if
   if (endian /= order) error stop 'byte order reference'
   call penf_init()
   if (.not. is_initialized .or. endian /= order) error stop 'repeated initialization'
   one4 = 1._R4P
   one8 = 1._R8P
   step4 = one4
   step8 = one8
   count4 = 0
   do
      next4 = one4+step4/2
      if (next4 == one4) exit
      step4 = step4/2
      count4 = count4+1
      if (count4 > 100) error stop 'real32 experiment did not terminate'
   end do
   count8 = 0
   do
      next8 = one8+step8/2
      if (next8 == one8) exit
      step8 = step8/2
      count8 = count8+1
      if (count8 > 200) error stop 'real64 experiment did not terminate'
   end do
   if (step4 /= epsilon(one4) .or. count4+1 /= digits(one4)) error stop 'measured real32 roundoff'
   if (step8 /= epsilon(one8) .or. count8+1 /= digits(one8)) error stop 'measured real64 roundoff'
   print '(a,4i4)', 'Integer storage bits:',BII1P,BII2P,BII4P,BII8P
   print '(a,i0,a,es12.4)', 'R4P significand bits=',count4+1,' measured epsilon=',step4
   print '(a,i0,a,es12.4)', 'R8P significand bits=',count8+1,' measured epsilon=',step8
   print '(a,i0,a)', 'Endian code=',endian,' (verified from the bytes of 0x01020304).'
   print '(a)', 'PASS penf-machine-reference'
end program machine_reference
