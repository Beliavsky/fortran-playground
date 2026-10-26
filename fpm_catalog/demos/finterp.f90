program main
   use iso_fortran_env, only: real64
   use linear_interpolation_module, only: linear_interp_1d
   implicit none
   type(linear_interp_1d) :: interpolator
   real(real64) :: value
   integer :: status
   call interpolator%initialize([0.0_real64,1.0_real64], [2.0_real64,4.0_real64], status)
   if (status /= 0) error stop 'initialization failed'
   call interpolator%evaluate(0.25_real64, value)
   if (abs(value-2.5_real64) > 1.e-12_real64) error stop 'incorrect interpolation'
   print *, 'Interpolated value:', value
   print *, 'PASS finterp'
end program main
