! Independent MIT consumer; see licenses/grids-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64, int64
   use ieee_arithmetic, only: ieee_is_finite
   use stdlib_math, only: is_close, all_close
   implicit none
   logical,parameter :: reference(17,17)=reshape([ &
      .true., .true., .false., .false., .false., .false., .false., .false., &
      .false., .false., .false., .false., .false., .false., .false., .false., &
      .false., .true., .true., .false., .false., .false., .false., .false., &
      .false., .false., .false., .false., .false., .false., .false., .false., &
      .false., .false., .false., .false., .true., .false., .false., .false., &
      .false., .false., .false., .false., .false., .false., .false., .false., &
      .false., .false., .false., .false., .false., .false., .true., .false., &
      .false., .false., .false., .false., .false., .false., .false., .false., &
      .false., .false., .false., .false., .false., .false., .false., .false., &
      .true., .false., .false., .false., .false., .false., .false., .false., &
      .false., .false., .false., .false., .false., .false., .false., .false., &
      .false., .false., .true., .false., .false., .false., .false., .false., &
      .false., .false., .false., .false., .false., .false., .false., .false., &
      .false., .false., .false., .false., .true., .false., .false., .false., &
      .false., .false., .false., .false., .false., .false., .false., .false., &
      .false., .false., .false., .false., .false., .false., .true., .false., &
      .false., .false., .false., .false., .false., .false., .false., .false., &
      .false., .false., .false., .false., .false., .false., .false., .false., &
      .true., .false., .false., .false., .false., .false., .false., .false., &
      .false., .false., .false., .false., .false., .false., .false., .false., &
      .false., .false., .true., .false., .false., .false., .false., .false., &
      .false., .false., .false., .false., .false., .false., .false., .false., &
      .false., .false., .false., .false., .true., .false., .false., .false., &
      .false., .false., .false., .false., .false., .false., .false., .false., &
      .false., .false., .false., .false., .false., .false., .true., .false., &
      .false., .false., .false., .false., .false., .false., .false., .false., &
      .false., .false., .false., .false., .false., .false., .false., .false., &
      .true., .false., .false., .false., .false., .false., .false., .false., &
      .false., .false., .false., .false., .false., .false., .false., .false., &
      .false., .false., .true., .false., .false., .false., .false., .false., &
      .false., .false., .false., .false., .false., .false., .false., .false., &
      .false., .false., .false., .false., .true., .false., .false., .false., &
      .false., .false., .false., .false., .false., .false., .false., .false., &
      .false., .false., .false., .false., .false., .false., .true., .true., &
      .false., .false., .false., .false., .false., .false., .false., .false., &
      .false., .false., .false., .false., .false., .false., .false., .true., &
      .true. ],[17,17])

   real(real64) :: a,b,x(17),nan,m(2,2),other(2,2)
   complex(real64) :: z(2,2),w(2,2)
   logical :: actual(17)
   integer :: i,j
   x=[(real(i,real64)/4,i=-8,8)]
   do j=1,17
      b=x(j); actual=is_close(x,b,rel_tol=0.125_real64,abs_tol=0.0625_real64)
      if(any(actual.neqv.reference(:,j))) error stop 'Exact rational tolerance table'
      do i=1,17
         a=x(i)
         if(is_close(a,b,rel_tol=0.125_real64,abs_tol=0.0625_real64).neqv.reference(i,j)) &
            error stop 'Scalar tolerance truth table'
         if(is_close(b,a,rel_tol=0.125_real64,abs_tol=0.0625_real64).neqv.reference(i,j)) &
            error stop 'Symmetric tolerance truth table'
      end do
   end do
   m=1; other=m; other(2,1)=1.125_real64
   if(.not.all_close(m,other,rel_tol=0._real64,abs_tol=0.125_real64)) error stop 'Inclusive tolerance boundary'
   other(2,1)=1.25_real64
   if(all_close(m,other,rel_tol=0._real64,abs_tol=0.125_real64)) error stop 'Outside tolerance'
   z=cmplx(m,m,real64); w=z; w(2,2)=cmplx(1.125_real64,1.125_real64,real64)
   if(.not.all_close(z,w,rel_tol=0._real64,abs_tol=0.125_real64)) error stop 'Componentwise complex policy'
   w(2,2)=cmplx(1._real64,1.25_real64,real64)
   if(all_close(z,w,rel_tol=0._real64,abs_tol=0.125_real64)) error stop 'Complex imaginary mismatch'
   block
      use ieee_arithmetic, only: ieee_value, ieee_quiet_nan
      nan=ieee_value(0._real64,ieee_quiet_nan)
   end block
   if(is_close(nan,nan)) error stop 'Default NaN policy'
   if(.not.is_close(nan,nan,equal_nan=.true.)) error stop 'Explicit equal NaN policy'
   if(is_close(nan,1._real64,equal_nan=.true.)) error stop 'One NaN policy'
   print '(a)', 'Exact rational tolerance pairs: 289; matrix, componentwise complex and NaN policies checked'
   print '(a)', 'PASS stdlib-tolerance-comparison-reference'
end program
