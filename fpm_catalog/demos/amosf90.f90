program complex_bessel_functions
   use iso_fortran_env, only: dp=>real64
   use ieee_arithmetic, only: ieee_is_finite
   use amos, only: f90_zbesj, f90_zbesi, f90_zbesk
   implicit none
   complex(dp) :: z, j(1), modified_i(1), modified_k(1), reference_j, reference_i, reference_k
   real(dp), parameter :: nu=0.3_dp, pi=acos(-1.0_dp)
   integer :: underflows, status
   z=cmplx(1.0_dp,0.5_dp,dp)
   call f90_zbesj(z,nu,1,1,j,underflows,status)
   if(status/=0 .or. underflows/=0) error stop 'J calculation failed'
   call f90_zbesi(z,nu,1,1,modified_i,underflows,status)
   if(status/=0 .or. underflows/=0) error stop 'I calculation failed'
   call f90_zbesk(z,0.5_dp,1,1,modified_k,underflows,status)
   if(status/=0 .or. underflows/=0) error stop 'K calculation failed'
   reference_j=power_series(z,nu,-1)
   reference_i=power_series(z,nu,1)
   reference_k=sqrt(pi/(2*z))*exp(-z)
   if(.not.all(ieee_is_finite([real(j(1)),aimag(j(1)),real(modified_i(1)),aimag(modified_i(1)), &
      real(modified_k(1)),aimag(modified_k(1))]))) error stop 'Nonfinite result'
   if(abs(j(1)-reference_j)>1.e-11_dp) error stop 'J disagrees with independent series'
   if(abs(modified_i(1)-reference_i)>1.e-11_dp) error stop 'I disagrees with independent series'
   if(abs(modified_k(1)-reference_k)>1.e-11_dp) error stop 'K half-order identity failed'
   print '(a)', 'Complex argument z = 1 + 0.5i; noninteger orders'
   print '(a,2f18.12)', 'J_0.3(z), real/imag: ',real(j(1)),aimag(j(1))
   print '(a,2f18.12)', 'I_0.3(z), real/imag: ',real(modified_i(1)),aimag(modified_i(1))
   print '(a,2f18.12)', 'K_0.5(z), real/imag: ',real(modified_k(1)),aimag(modified_k(1))
   print *, 'PASS amosf90'
contains
   function power_series(x,order,sign_factor) result(value)
      complex(dp),intent(in)::x
      real(dp),intent(in)::order
      integer,intent(in)::sign_factor
      complex(dp)::value,term,total
      integer::k
      term=cmplx(1.0_dp,0.0_dp,dp);total=term
      do k=1,60
         term=term*(sign_factor*x*x/4)/(k*(order+k))
         total=total+term
         if(abs(term)<epsilon(1.0_dp)*abs(total)) exit
      end do
      value=(x/2)**order*total/gamma(order+1)
   end function power_series
end program complex_bessel_functions
