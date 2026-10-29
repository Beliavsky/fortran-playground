program demo_equation_parser
   use, intrinsic :: iso_fortran_env, only: real64
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   use FEQParse, only: EquationParser
   implicit none
   type(EquationParser) :: gaussian, polynomial
   real(real64) :: xyz(3), actual, expected, actual_poly, expected_poly
   integer :: i

   gaussian = EquationParser('f = exp(-(x^2 + y^2 + z^2))', ['x', 'y', 'z'])
   polynomial = EquationParser('g = (x + 2*y)^2 + z', ['x', 'y', 'z'])
   print '(a)', 'x          parsed Gaussian       direct Gaussian'
   do i = -3, 3
      xyz = [real(i, real64)/2.0_real64, 0.25_real64, -0.5_real64]
      actual = gaussian%evaluate(xyz)
      expected = exp(-sum(xyz**2))
      actual_poly = polynomial%evaluate(xyz)
      expected_poly = (xyz(1) + 2.0_real64*xyz(2))**2 + xyz(3)
      if (.not. ieee_is_finite(actual) .or. .not. ieee_is_finite(actual_poly)) error stop 'nonfinite evaluation'
      if (abs(actual - expected) > 1.e-12_real64) error stop 'Gaussian evaluation'
      if (abs(actual_poly - expected_poly) > 1.e-12_real64) error stop 'polynomial evaluation'
      print '(f6.2, 2f22.14)', xyz(1), actual, expected
   end do
   print '(a)', 'Polynomial precedence and multivariable evaluation also checked.'
   print '(a)', 'PASS feq-parse'
end program demo_equation_parser
