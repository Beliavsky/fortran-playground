program main
   use iso_fortran_env, only: int32, real64
   use m_npy, only: save_npy
   implicit none
   real(real64) :: matrix(2,3), recovered(2,3)
   character(8) :: magic
   character(:), allocatable :: header
   integer(int32) :: header_length
   integer :: unit, i, bytes
   matrix = reshape([1.0_real64,2.0_real64,3.0_real64,4.0_real64,5.0_real64,6.0_real64],[2,3])
   call save_npy('matrix.npy',matrix)
   open(newunit=unit,file='matrix.npy',access='stream',form='unformatted',status='old',action='read')
   read(unit) magic, header_length
   if (magic /= achar(147)//'NUMPY'//achar(2)//achar(0)) error stop 'NPY magic/version'
   if (header_length < 1 .or. header_length > 4096) error stop 'NPY header length'
   allocate(character(header_length) :: header)
   read(unit) header
   if (index(header,'<f8') == 0 .or. index(header,'True') == 0) error stop 'dtype/order'
   read(unit) recovered
   close(unit)
   if (any(recovered /= matrix)) error stop 'matrix payload'
   inquire(file='matrix.npy',size=bytes)
   if (bytes /= 12+header_length+storage_size(matrix)/8*size(matrix)) error stop 'file size'
   print '(a)', 'Matrix written to matrix.npy:'
   do i = 1, 2
      print '(3f7.2)',matrix(i,:)
   end do
   print '(a)', 'NPY header: '//trim(header)
   print '(a,i0)', 'File size in bytes: ', bytes
   print '(a)', 'PASS npy-for-fortran'
end program main
