program demo_calculator
   use M_calculator, only: dnum0
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   double precision :: result

   result = dnum0('radius=3')
   if (result /= 3.d0) error stop 'Variable assignment failed'
   result = dnum0('area=acos(-1)*radius**2')
   if (.not. ieee_is_finite(result)) error stop 'Nonfinite expression result'
   if (abs(result - acos(-1.d0)*9.d0) > 1.d-10) error stop 'Expression check failed'
   print '(a,f14.8)', 'Area for radius 3: ', result
   result = dnum0('sqrt(81)+2**3')
   if (abs(result-17.d0) > 1.d-12) error stop 'Arithmetic check failed'
   print '(a,f10.4)', 'sqrt(81)+2**3 = ', result
   print *, 'PASS m_calculator'
end program demo_calculator
