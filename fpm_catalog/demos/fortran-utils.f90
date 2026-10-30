! A cubic is reproduced by the spline, including its first two derivatives.
program main
   use types, only: dp
   use mesh, only: linspace, meshexp
   use splines, only: spline3ders
   use sorting, only: sort
   implicit none
   real(dp) :: x(9), y(9), query(17), value(17), derivative(17), second(17), stretched(9)
   real(dp) :: errors(3), ratio
   integer :: values(6)
   x = linspace(0.0_dp,1.0_dp,size(x))
   y = x**3-2.0_dp*x+1.0_dp
   query = linspace(0.0_dp,1.0_dp,size(query))
   call spline3ders(x,y,query,value,derivative,second)
   errors = [maxval(abs(value-(query**3-2.0_dp*query+1.0_dp))), &
      maxval(abs(derivative-(3.0_dp*query**2-2.0_dp))), maxval(abs(second-6.0_dp*query))]
   print '(a,3es12.4)', 'Maximum errors: value, first derivative, second derivative: ', errors
   if (any(errors > 1.0e-10_dp)) error stop 'Cubic reproduction failed'
   stretched = meshexp(0.0_dp,1.0_dp,4.0_dp,8)
   if (abs(stretched(1)) > 1.0e-12_dp .or. abs(stretched(9)-1.0_dp) > 1.0e-12_dp) &
      error stop 'Incorrect mesh endpoints'
   if (any(stretched(2:) <= stretched(:8))) error stop 'Mesh is not increasing'
   ratio = (stretched(9)-stretched(8))/(stretched(2)-stretched(1))
   if (abs(ratio-4.0_dp) > 1.0e-12_dp) error stop 'Incorrect mesh spacing ratio'
   print '(a,f8.4)', 'Last/first mesh spacing: ', ratio
   values = [9,-2,5,5,0,3]
   call sort(values)
   if (any(values /= [-2,0,3,5,5,9])) error stop 'Incorrect sort'
   print '(a,6i4)', 'Sorted integers: ', values
   print '(a)', 'PASS fortran-utils'
end program main
