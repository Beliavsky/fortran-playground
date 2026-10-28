program demo_zlib
   use zlib
   implicit none(type, external)
   character(:), allocatable :: original, compressed, restored
   integer(z_ulong) :: input_size, compressed_size, output_size
   integer :: status

   original = repeat('Fortran scientific computing. ', 100)
   input_size = len(original, kind=z_ulong)
   compressed_size = compress_bound(input_size)
   allocate(character(len=compressed_size) :: compressed)
   status = compress(compressed, compressed_size, original, input_size)
   if (status /= Z_OK) error stop 'Compression failed'
   output_size = input_size
   allocate(character(len=output_size) :: restored)
   status = uncompress(restored, output_size, compressed, compressed_size)
   if (status /= Z_OK) error stop 'Decompression failed'
   if (output_size /= input_size .or. restored /= original) error stop 'Compression round trip failed'
   if (compressed_size >= input_size) error stop 'Expected repeated text to compress'
   print '(a,i0)', 'Original bytes:   ', input_size
   print '(a,i0)', 'Compressed bytes: ', compressed_size
   print '(a)', 'Decompressed text matches the original.'
   print *, 'PASS fortran-zlib'
end program demo_zlib
