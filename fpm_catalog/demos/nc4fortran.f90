program main
   use iso_fortran_env, only: real64
   use nc4fortran, only: netcdf_file
   implicit none
   type(netcdf_file) :: file
   real(real64) :: original(2,3), restored(2,3)
   character(32) :: units
   integer :: unit
   original = reshape([1.0_real64, 2.0_real64, 3.0_real64, &
      4.0_real64, 5.0_real64, 6.0_real64], [2,3])
   call file%open('measurements.nc', action='w')
   call file%write('temperature', original, ['x','y'])
   call file%write_attribute('temperature', 'units', 'kelvin')
   call file%close()
   call file%open('measurements.nc', action='r')
   call file%read('temperature', restored)
   call file%read_attribute('temperature', 'units', units)
   call file%close()
   if (any(abs(restored-original) > 1.0e-12_real64)) error stop 'array round trip'
   if (trim(units) /= 'kelvin') error stop 'attribute round trip'
   print *, 'Restored array shape:', shape(restored)
   print *, 'Sum:', sum(restored), ' units: ', trim(units)
   open(newunit=unit, file='measurements.nc', status='old')
   close(unit, status='delete')
   print *, 'PASS nc4fortran'
end program
