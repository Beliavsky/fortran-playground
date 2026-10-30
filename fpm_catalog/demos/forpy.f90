! Python and NumPy are installed in the playground sandbox.
! Locally, link with the flags from: python3-config --embed --ldflags
program main
   use iso_fortran_env, only: real64
   use ieee_arithmetic, only: ieee_is_finite
   use forpy_mod
   implicit none
   type(module_py) :: numpy, linalg
   type(ndarray) :: array
   type(tuple) :: arguments
   type(object) :: result
   real(real64) :: values(2,3), total, norm
   values = reshape([1.0_real64,2.0_real64,3.0_real64,4.0_real64,5.0_real64,6.0_real64], [2,3])
   call check(forpy_initialize())
   call check(import_py(numpy, 'numpy'))
   call check(import_py(linalg, 'numpy.linalg'))
   call check(ndarray_create(array, values))
   call check(tuple_create(arguments, 1))
   call check(arguments%setitem(0, array))
   call check(call_py(result, numpy, 'sum', arguments))
   call check(cast(total, result))
   call result%destroy()
   call check(call_py(result, linalg, 'norm', arguments))
   call check(cast(norm, result))
   if (.not. ieee_is_finite(total) .or. .not. ieee_is_finite(norm)) error stop 'Nonfinite NumPy result'
   if (abs(total-sum(values)) > 1.0e-12_real64) error stop 'NumPy sum mismatch'
   if (abs(norm-sqrt(sum(values**2))) > 1.0e-12_real64) error stop 'NumPy norm mismatch'
   print '(a,f12.8)', 'NumPy sum:  ', total
   print '(a,f12.8)', 'NumPy norm: ', norm
   call result%destroy()
   call arguments%destroy()
   call array%destroy()
   call linalg%destroy()
   call numpy%destroy()
   call forpy_finalize()
   print '(a)', 'PASS forpy'
contains
   subroutine check(code)
      integer, intent(in) :: code
      if (code /= 0) then
         call err_print()
         print '(a,i0)', 'Forpy error: ', code
         error stop 'Python operation failed'
      end if
   end subroutine check
end program main
