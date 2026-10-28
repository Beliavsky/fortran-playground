program demo_h5fortran
   use iso_fortran_env, only: real64
   use h5fortran, only: h5write, h5read, h5write_attr, h5read_attr
   implicit none
   real(real64) :: original(2,3), restored(2,3)
   character(32) :: units
   integer :: i

   original = reshape([1._real64, 2._real64, 3._real64, 4._real64, 5._real64, 6._real64], [2,3])
   call h5write('sample.h5', '/temperature', original)
   call h5write_attr('sample.h5', '/temperature', 'units', 'kelvin')
   call h5read('sample.h5', '/temperature', restored)
   call h5read_attr('sample.h5', '/temperature', 'units', units)
   if (any(restored /= original)) error stop 'HDF5 matrix round trip failed'
   if (units /= 'kelvin') error stop 'HDF5 attribute round trip failed'
   print '(a)', 'Matrix read from sample.h5 (units: '//trim(units)//')'
   do i = 1, 2
      print '(3f8.2)', restored(i,:)
   end do
   print *, 'PASS h5fortran'
end program demo_h5fortran
