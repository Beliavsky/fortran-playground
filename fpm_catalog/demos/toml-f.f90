! Parse a small TOML document and retrieve its integer value.
program demo
   use tomlf, only: toml_table, toml_error, toml_parse, get_value
   implicit none
   type(toml_table), allocatable :: table
   type(toml_error), allocatable :: error
   integer :: answer, status
   call toml_parse(table, 'answer = 42', error=error)
   if (allocated(error)) error stop 'TOML parsing failed'
   call get_value(table, 'answer', answer, stat=status)
   if (status /= 0 .or. answer /= 42) error stop 'incorrect TOML value'
   print '(a,i0)', 'PASS toml-f answer=', answer
end program demo
