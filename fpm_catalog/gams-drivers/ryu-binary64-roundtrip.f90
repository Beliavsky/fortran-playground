! Original GAMS A6 API driver. MIT: licenses/arithmetic-drivers-MIT.txt.
! This tests finite round trips, not a proof of globally shortest decimal strings.
program main
   use iso_fortran_env, only: int64, real64
   use ryu, only: d2shortest
   implicit none
   integer, parameter :: exponents(*) = [0,1,2,10,511,1022,1023,1024,1535,2045,2046]
   integer(int64), parameter :: mantissas(*) = [0_int64,1_int64,2_int64, &
      2_int64**51-1,2_int64**51,2_int64**52-1]
   integer :: i, j, sign, count, ios
   integer(int64) :: bits
   real(real64) :: value, restored
   character(:), allocatable :: text
   count = 0
   if (storage_size(value) /= 64 .or. radix(value) /= 2 .or. digits(value) /= 53) &
      error stop 'requires IEEE binary64 layout'
   do i = 1, size(exponents)
      do j = 1, size(mantissas)
         do sign = 0, 1
            bits = ior(shiftl(int(exponents(i),int64),52), mantissas(j))
            if (sign == 1) bits = ibset(bits,63)
            value = transfer(bits, value)
            text = d2shortest(value)
            read(text,*,iostat=ios) restored
            if (ios /= 0) then
               print '(a)', 'Unreadable decimal: '//text
               error stop 'decimal parse'
            end if
            if (transfer(restored,0_int64) /= bits) then
               print '(a,z16.16,a,a)', 'Round-trip mismatch for bits ', bits, ': ', text
               error stop 'binary64 round trip'
            end if
            count = count + 1
         end do
      end do
   end do
   if (count /= 132) error stop 'case count'
   if (d2shortest(0.0_real64) /= '0.0') error stop 'positive zero spelling'
   if (d2shortest(-0.0_real64) /= '-0.0') error stop 'negative zero spelling'
   print '(a)', 'Smallest subnormal: '//d2shortest(transfer(1_int64,value))
   print '(a)', 'Smallest normal: '//d2shortest(tiny(value))
   print '(a)', 'Largest finite: '//d2shortest(huge(value))
   print '(a)', 'Negative zero: '//d2shortest(-0.0_real64)
   print '(a,i0)', 'Finite binary64 values recovered with identical bits: ', count
   print '(a)', 'NaN/infinity spelling, all bit patterns and shortest-length optimality are outside this example.'
   print '(a)', 'PASS ryu-binary64-roundtrip'
end program
