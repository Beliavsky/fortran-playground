! Independent API consumer; MIT: licenses/roots-splines-quadrature-drivers-MIT.txt.
program spline_reference
   use types, only: dp
   use splines, only: spline3ders
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer, parameter :: sizes(*) = [5,9,17,9]
   real(dp), parameter :: coefficients(0:3,4) = reshape([ &
      1._dp,0._dp,0._dp,0._dp, -1._dp,2._dp,0._dp,0._dp, &
      .5_dp,-2._dp,3._dp,0._dp, -1._dp,2._dp,-.5_dp,1._dp],[4,4])
   real(dp), allocatable :: x(:),y(:)
   real(dp) :: q(65),value(65),first(65),second(65),only(65),reference(65,3),errors(3),c(0:3)
   integer :: grid,polynomial,i,n,cases
   q = [(-1._dp+real(i,dp)/32,i=0,64)]
   errors = 0._dp
   cases = 0
   do grid = 1,4
      n = sizes(grid)
      allocate(x(n),y(n))
      x = [(-1._dp+2*real(i,dp)/(n-1),i=0,n-1)]
      if (grid == 4) x = [-1._dp,-.875_dp,-.625_dp,-.25_dp,0._dp,.1875_dp,.5_dp,.75_dp,1._dp]
      do polynomial = 1,4
         c = coefficients(:,polynomial)
         y = ((c(3)*x+c(2))*x+c(1))*x+c(0)
         reference(:,1) = ((c(3)*q+c(2))*q+c(1))*q+c(0)
         reference(:,2) = (3*c(3)*q+2*c(2))*q+c(1)
         reference(:,3) = 6*c(3)*q+2*c(2)
         call spline3ders(x,y,q,value,first,second)
         if (.not. all(ieee_is_finite(value)) .or. .not. all(ieee_is_finite(first)) &
            .or. .not. all(ieee_is_finite(second))) error stop 'nonfinite spline values/derivatives'
         errors = max(errors,[maxval(abs(value-reference(:,1))),maxval(abs(first-reference(:,2))), &
            maxval(abs(second-reference(:,3)))])
         if (any(errors > 5.e-10_dp)) error stop 'polynomial spline reproduction'
         call spline3ders(x,y,q,dynew=only)
         if (.not. all(ieee_is_finite(only)) .or. maxval(abs(only-first)) > 5.e-12_dp) &
            error stop 'first derivative optional output'
         call spline3ders(x,y,q,d2ynew=only)
         if (.not. all(ieee_is_finite(only)) .or. maxval(abs(only-second)) > 5.e-12_dp) &
            error stop 'second derivative optional output'
         call spline3ders(x,y,q(65:1:-1),ynew=only)
         if (.not. all(ieee_is_finite(only)) .or. maxval(abs(only-value(65:1:-1))) > 5.e-12_dp) &
            error stop 'reversed query order and value-only output'
         cases = cases+1
      end do
      deallocate(x,y)
   end do
   if (cases /= 16) error stop 'spline fixture count'
   print '(a)', '16 polynomial/grid fixtures, 65 queries each, 3120 value/derivative references.'
   print '(a,3es12.4)', 'Maximum errors: value, first derivative, second derivative: ',errors
   print '(a)', 'Uniform/nonuniform knots, endpoints, optional outputs and reversed query order checked.'
   print '(a)', 'PASS fortran-utils-spline-reference'
end program spline_reference
