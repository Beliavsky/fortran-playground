program main
   use function_parser, only: fparser
   use iso_fortran_env, only: real64
   implicit none
   type(fparser) :: expression
   real(real64) :: result
   call expression%parse('sin(x)^2 + cos(x)^2', ['x'])
   if (expression%error()) error stop 'expression parsing failed'
   call expression%evaluate([0.7_real64], result)
   if (expression%error() .or. abs(result-1.0_real64) > 1.e-12_real64) error stop 'incorrect evaluation'
   print *, 'Expression value:', result
   call expression%destroy()
   print *, 'PASS fortran_function_parser'
end program main
