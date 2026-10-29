program main
   use erloff, only: error_list_t, fatal_t, module_t, procedure_t, &
      OUT_OF_BOUNDS, INPUTS, size
   use iso_varying_string, only: char
   implicit none
   type(error_list_t) :: errors, bounds
   errors = errors%with_error_appended(fatal_t(OUT_OF_BOUNDS, &
      module_t('validation'), procedure_t('check'), 'Temperature must be positive'))
   errors = errors%with_error_appended(fatal_t(INPUTS, &
      module_t('validation'), procedure_t('check'), 'Name must not be empty'))
   if (size(errors) /= 2) error stop 'error count'
   bounds = errors.ofType.OUT_OF_BOUNDS
   if (size(bounds) /= 1) error stop 'filtered count'
   if (index(char(bounds%to_string()), 'Temperature must be positive') == 0) &
      error stop 'missing diagnostic'
   if (index(char(errors%to_string()), 'Name must not be empty') == 0) &
      error stop 'missing second error'
   print '(a)', char(errors%to_string())
   print *, 'Bounds errors:', size(bounds)
   print *, 'PASS erloff'
end program
