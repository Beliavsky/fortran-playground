program demo_named_columns
   use df_fortranDF, only: data_frame
   use df_precision, only: rk
   implicit none
   type(data_frame) :: table
   real(rk), allocatable :: temperatures(:)
   real(rk) :: mean

   call table%new()
   call table%append([1, 2, 3, 4], 'id')
   call table%append([character(5) :: 'north', 'south', 'east', 'west'], 'site')
   call table%append([10.0_rk, 12.0_rk, 14.0_rk, 16.0_rk], 'temp_c')
   if (any(table%geti('id') /= [1, 2, 3, 4])) error stop 'integer column'
   if (trim(table%getch('site', 2)) /= 'south') error stop 'character column'
   temperatures = table%getr('temp_c')
   mean = sum(temperatures)/size(temperatures)
   if (abs(mean - 13.0_rk) > 1.e-12_rk) error stop 'initial mean'
   print '(a, f8.2)', 'Initial mean temperature (C): ', mean

   call table%setr('temp_c', temperatures + 0.5_rk)
   temperatures = table%getr('temp_c')
   if (maxval(abs(temperatures - [10.5_rk, 12.5_rk, 14.5_rk, 16.5_rk])) > 1.e-12_rk) &
      error stop 'updated column'
   mean = sum(temperatures)/size(temperatures)
   if (abs(mean - 13.5_rk) > 1.e-12_rk) error stop 'updated mean'
   print '(a, f8.2)', 'Mean after calibration (C):   ', mean
   call table%destroy()
   print '(a)', 'PASS fortrandf'
end program demo_named_columns
