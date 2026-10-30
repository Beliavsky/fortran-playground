! Based on the author's doc/examples/integration.f90, with independent checks.
module playground_fgsl_integrand
   use, intrinsic :: iso_c_binding, only: c_double, c_ptr, c_f_pointer
   implicit none
contains
   function integrand(x, parameters) bind(c) result(y)
      real(c_double), value :: x
      type(c_ptr), value :: parameters
      real(c_double) :: y
      real(c_double), pointer :: alpha
      call c_f_pointer(parameters, alpha)
      y = log(alpha*x)/sqrt(x)
   end function integrand
end module playground_fgsl_integrand

program main
   use fgsl
   use playground_fgsl_integrand
   use, intrinsic :: iso_c_binding, only: c_loc
   use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
   implicit none
   integer(fgsl_size_t), parameter :: limit=1000
   real(fgsl_double), target :: alpha
   real(fgsl_double) :: value, estimate
   integer(fgsl_int) :: status
   type(fgsl_function) :: function
   type(fgsl_integration_workspace) :: workspace
   alpha = 1.0_fgsl_double
   function = fgsl_function_init(integrand, c_loc(alpha))
   workspace = fgsl_integration_workspace_alloc(limit)
   if (.not. fgsl_well_defined(workspace)) error stop 'Workspace allocation failed'
   status = fgsl_integration_qags(function, 0.0_fgsl_double, 1.0_fgsl_double, &
      0.0_fgsl_double, 1.0e-8_fgsl_double, limit, workspace, value, estimate)
   call fgsl_function_free(function)
   call fgsl_integration_workspace_free(workspace)
   if (status /= fgsl_success) error stop 'Adaptive integration failed'
   if (.not. ieee_is_finite(value) .or. .not. ieee_is_finite(estimate)) error stop 'Nonfinite result'
   if (abs(value+4.0_fgsl_double) > 1.0e-7_fgsl_double) error stop 'Integral differs from exact -4'
   if (estimate < 0.0_fgsl_double .or. estimate > 1.0e-7_fgsl_double) error stop 'Error estimate too large'
   print '(a,f18.12)', 'Integral of log(x)/sqrt(x) on [0,1]: ', value
   print '(a,es12.4)', 'Estimated absolute error: ', estimate
   print '(a)', 'Exact integral: -4; PASS fgsl'
end program main
