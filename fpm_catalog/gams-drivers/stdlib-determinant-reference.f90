! Independent MIT consumer; see licenses/statistics-services-ten-drivers-MIT.txt.
program main
   use iso_fortran_env, only: real64
   use ieee_arithmetic, only: ieee_is_finite
   use stdlib_linalg, only: det,linalg_state_type
   implicit none
   type(linalg_state_type) :: state
   real(real64) :: lower(3,3),upper(3,3),a(3,3),original(3,3),row(3),actual,expected
   integer :: t,i
   do t=1,96
      lower=0
      upper=0
      do i=1,3
         lower(i,i)=1
         upper(i,i)=i+1
      end do
      lower(2,1)=mod(t,5)-2
      lower(3,1)=mod(t/5,5)-2
      lower(3,2)=mod(t/7,5)-2
      upper(1,2)=mod(t/3,7)-3
      upper(1,3)=mod(t/11,7)-3
      upper(2,3)=mod(t/13,7)-3
      a=matmul(lower,upper)
      if(mod(t,2)==0) then
         row=a(1,:)
         a(1,:)=a(3,:)
         a(3,:)=row
      end if
      ! Independent six-term determinant, not LU or a package factorization.
      expected=a(1,1)*(a(2,2)*a(3,3)-a(2,3)*a(3,2)) &
         -a(1,2)*(a(2,1)*a(3,3)-a(2,3)*a(3,1)) &
         +a(1,3)*(a(2,1)*a(3,2)-a(2,2)*a(3,1))
      original=a
      actual=det(a,err=state)
      if(.not.state%ok().or..not.ieee_is_finite(actual)) error stop 'Determinant status'
      if(abs(actual-expected)>1.e-11_real64*abs(expected)) error stop 'Six-term determinant oracle'
      if(any(a/=original)) error stop 'Input overwritten'
   end do
   print '(a)', '96 nonsingular real 3x3 determinants; positive/negative parity, six-term oracle, input preservation'
   print '(a)', 'PASS stdlib-determinant-reference'
end program
