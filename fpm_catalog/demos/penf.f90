program main
   use penf, only: penf_init, I4P, R8P, FR8P, str, strz, cton, byte_size
   implicit none
   integer(I4P) :: value, recovered, status
   real(R8P) :: x, y
   character(:), allocatable :: text, padded

   call penf_init()
   value = 42_I4P
   text = str(value)
   recovered = cton(text, knd=0_I4P, error=status)
   if (status /= 0 .or. recovered /= value) error stop 'integer round trip'
   print '(a)', 'Integer string: '//trim(text)
   x = -1.25_R8P
   text = str(x)
   y = cton(text, knd=0.0_R8P, error=status)
   if (status /= 0 .or. abs(y-x) > 1.0e-14_R8P) error stop 'real round trip'
   print '(a)', 'Real string: '//trim(text)
   padded = strz(value, nz_pad=5)
   if (trim(padded) /= '00042') error stop 'zero padding'
   print '(a)', 'Padded integer: '//trim(padded)
   if (byte_size(x) /= storage_size(x)/8) error stop 'byte size'
   print '(a,i0)', 'Real value size in bytes: ', byte_size(x)
   print '(a)', 'PENF real format:'
   print FR8P, x
   print '(a)', 'PASS penf'
end program main
