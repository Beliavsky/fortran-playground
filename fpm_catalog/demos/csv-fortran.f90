program main
   use csv_module, only: csv_file
   use iso_fortran_env, only: real64
   implicit none
   type(csv_file) :: file
   real(real64), allocatable :: column(:)
   logical :: ok
   call file%open('values.csv', n_cols=2, status_ok=ok)
   if (.not. ok) error stop 'open failed'
   call file%add(['x','y'])
   call file%next_row()
   call file%add([1.0_real64,2.0_real64])
   call file%next_row()
   call file%add([3.0_real64,6.0_real64])
   call file%next_row()
   call file%close(ok)
   if (.not. ok) error stop 'close failed'
   call file%read('values.csv', header_row=1, status_ok=ok)
   if (.not. ok) error stop 'read failed'
   call file%get(2, column, ok)
   if (.not. ok) error stop 'missing column'
   if (size(column) /= 2) error stop 'incorrect row count'
   if (any(abs(column-[2.0_real64,6.0_real64]) > 1.e-12_real64)) error stop 'incorrect values'
   print *, 'CSV y column:', column
   print *, 'PASS csv-fortran'
end program main
