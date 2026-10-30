program main
   use iso_fortran_env, only: real64
   use m_lookup_table, only: LT_t, LT_create, LT_set_col_data, LT_get_col, LT_get_mcol
   implicit none
   type(LT_t) :: table
   real(real64) :: x(5), values(2), q, error
   integer :: i

   x = [(real(i, real64), i=0,4)]
   table = LT_create(0.0_real64, 4.0_real64, n_points=5, n_cols=2)
   call LT_set_col_data(table, 1, 2*x + 1)
   call LT_set_col_data(table, 2, x*x)
   q = 1.5_real64
   values = LT_get_mcol(table, q)
   if (maxval(abs(values - [4.0_real64, 2.5_real64])) > 1.0e-12_real64) error stop 'interpolation'
   error = abs(values(2) - q*q)
   if (abs(error - 0.25_real64) > 1.0e-12_real64) error stop 'quadratic interpolation error'
   if (abs(LT_get_col(table, 2, 3.0_real64) - 9) > 1.0e-12_real64) error stop 'grid point'
   if (abs(LT_get_col(table, 1, -1.0_real64) - 1) > 1.0e-12_real64) error stop 'lower clamp'
   if (abs(LT_get_col(table, 1, 5.0_real64) - 9) > 1.0e-12_real64) error stop 'upper clamp'
   print '(a,f4.1)', 'Query x: ', q
   print '(a,f6.3)', 'Linear function 2*x+1: ', values(1)
   print '(a,f6.3)', 'Interpolated x*x: ', values(2)
   print '(a,f6.3)', 'Absolute error versus x*x: ', error
   print '(a)', 'Grid-point and endpoint-clamping checks passed.'
   print '(a)', 'PASS lookup-table-fortran'
end program main
