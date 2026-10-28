program demo_paramcard
   use iso_fortran_env, only: real64
   use paramcard, only: paramcard_parse, paramcard_get, paramcard_summary
   implicit none
   integer :: steps
   real(real64) :: dt
   character(:), allocatable :: method

   ! Strings can also come from an input file or the playground's stdin box.
   call paramcard_parse('steps = 250')
   call paramcard_parse('method = rk4')
   call paramcard_get('steps', steps, 100)
   call paramcard_get('dt', dt, 0.01_real64)
   call paramcard_get('method', method, 'euler')
   if (steps /= 250 .or. dt /= 0.01_real64 .or. method /= 'rk4') error stop 'Parameter check failed'
   call paramcard_summary()
   print '(a,f8.3)', 'Simulated duration: ', steps*dt
   print *, 'PASS paramcard'
end program demo_paramcard
