program demo_zstd
   use zstd
   implicit none(type, external)
   character(:), allocatable :: original, compressed, restored
   integer(c_size_t) :: input_size, capacity, compressed_size, restored_size

   original = repeat('1.000,2.000,3.000,4.000'//new_line('a'), 128)
   input_size = len(original, kind=c_size_t)
   capacity = zstd_compress_bound(input_size)
   allocate(character(len=capacity) :: compressed)
   allocate(character(len=input_size) :: restored)
   compressed_size = zstd_compress(compressed, capacity, original, input_size, zstd_default_c_level())
   if (zstd_is_error(compressed_size)) error stop 'Zstandard compression failed'
   restored_size = zstd_decompress(restored, input_size, compressed, compressed_size)
   if (zstd_is_error(restored_size)) error stop 'Zstandard decompression failed'
   if (restored_size /= input_size .or. restored /= original) error stop 'Data round trip failed'
   if (compressed_size >= input_size) error stop 'Repeated data should compress'
   print '(a,i0)', 'Original CSV bytes: ', input_size
   print '(a,i0)', 'Compressed bytes:   ', compressed_size
   print '(a)', 'Decompressed data matches exactly.'
   print *, 'PASS fortran-zstd'
end program demo_zstd
