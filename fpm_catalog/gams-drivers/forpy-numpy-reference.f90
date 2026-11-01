! Independent MIT consumer; see licenses/interop-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64
   use ieee_arithmetic, only: ieee_is_finite
   use forpy_mod
   implicit none
   type(module_py) :: numpy,linalg
   type(ndarray) :: array
   type(tuple) :: arguments
   type(object) :: result
   real(real64),allocatable :: values(:,:)
   real(real64) :: total,squares,maximum,v,actual
   integer :: rows,cols,i,j,count
   count=0
   call check(forpy_initialize())
   call check(import_py(numpy,'numpy'))
   call check(import_py(linalg,'numpy.linalg'))
   do rows=1,5
      do cols=1,7
         allocate(values(rows,cols))
         total=0
         squares=0
         maximum=-huge(maximum)
         do j=1,cols
            do i=1,rows
               v=real(17*i-11*j,real64)/8
               values(i,j)=v
               total=total+v
               squares=squares+v*v
               maximum=max(maximum,v)
            end do
         end do
         call check(ndarray_create(array,values))
         call check(tuple_create(arguments,1))
         call check(arguments%setitem(0,array))
         call check(call_py(result,numpy,'sum',arguments))
         call check(cast(actual,result))
         if(.not.ieee_is_finite(actual) .or. actual/=total) error stop 'NumPy sum'
         call result%destroy()
         call check(call_py(result,numpy,'max',arguments))
         call check(cast(actual,result))
         if(.not.ieee_is_finite(actual) .or. actual/=maximum) error stop 'NumPy maximum'
         call result%destroy()
         call check(call_py(result,linalg,'norm',arguments))
         call check(cast(actual,result))
         if(.not.ieee_is_finite(actual)) error stop 'Nonfinite norm'
         if(abs(actual-sqrt(squares))>1.e-13_real64*max(1._real64,sqrt(squares))) error stop 'NumPy norm'
         call result%destroy()
         call arguments%destroy()
         call array%destroy()
         deallocate(values)
         count=count+3
      end do
   end do
   call linalg%destroy()
   call numpy%destroy()
   call forpy_finalize()
   print '(a,i0)', '35 embedded NumPy arrays; scalar-loop sum/max/Frobenius references: ',count
   print '(a)', 'PASS forpy-numpy-reference'
contains
   subroutine check(code)
      integer,intent(in) :: code
      if(code/=0) then
         call err_print()
         error stop 'Python API failure'
      end if
   end subroutine
end program
