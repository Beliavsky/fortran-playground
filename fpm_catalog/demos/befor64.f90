program demo_befor64
   use befor64, only: b64_init, b64_encode, b64_decode
   use penf, only: I4P
   implicit none
   character(:), allocatable :: encoded
   character(7) :: restored
   integer(I4P) :: values(3) = [1_I4P, -42_I4P, 12345_I4P], decoded(3)

   call b64_init()
   call b64_encode(s='Fortran', code=encoded)
   if (encoded /= 'Rm9ydHJhbg==') error stop 'Known Base64 encoding failed'
   print '(a)', 'Fortran -> '//encoded
   call b64_decode(code=encoded, s=restored)
   if (restored /= 'Fortran') error stop 'Text round trip failed'
   call b64_encode(n=values, code=encoded)
   call b64_decode(code=encoded, n=decoded)
   if (any(decoded /= values)) error stop 'Integer round trip failed'
   print '(a,3i8)', 'Recovered integers:', decoded
   print *, 'PASS befor64'
end program demo_befor64
