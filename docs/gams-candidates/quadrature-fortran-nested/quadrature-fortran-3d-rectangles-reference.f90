! Independent MIT consumer; see licenses/transforms-structures-ten-drivers-MIT.txt.
module integrand_data
   use quadrature_module, only: wp=>quadrature_wp, integration_class_3d
   implicit none
   integer :: power,calls
contains
   function integrand(me,x,y,z) result(f)
      class(integration_class_3d),intent(inout) :: me
      real(wp),intent(in) :: x,y,z
      real(wp) :: f
      calls=calls+1
      f=x**power*y**power*z**power
   end function
end module
program main
   use integrand_data
   use ieee_arithmetic, only: ieee_is_finite
   implicit none
   type(integration_class_3d) :: integrator
   real(wp) :: lower(3),upper(3),expected,actual,error
   integer :: method,domain,j,status,cases
   cases=0
   do method=6,10,2
      do domain=1,3
         do j=1,3
            lower(j)=-real(j,wp)/4; upper(j)=real(j+domain,wp)/4
         end do
         do power=0,3
            expected=1
            do j=1,3
               expected=expected*(upper(j)**(power+1)-lower(j)**(power+1))/real(power+1,wp)
            end do
            call integrator%initialize(integrand,lower(1),upper(1),lower(2),upper(2),lower(3),upper(3), &
               1.e-10_wp,1.e-10_wp,1.e-10_wp,method,method,method)
            calls=0; call integrator%integrate(actual,status,error)
            if(status/=1) error stop 'Nested quadrature status'
            if(calls<=0.or..not.ieee_is_finite(error).or.error<0) error stop 'Nested quadrature diagnostics'
            call check(actual,expected); cases=cases+1
         end do
      end do
   end do
   print '(a,i0)', 'Nested rectangular polynomial integrals and analytic product antiderivatives: ',cases
   print '(a)', 'PASS quadrature-fortran-3d-rectangles-reference'
contains
   subroutine check(actual,expected)
      real(wp),intent(in) :: actual,expected
      if(.not.ieee_is_finite(actual)) error stop 'Nonfinite result'
      if(abs(actual-expected)>2.e-9_wp*max(1._wp,abs(expected))) error stop 'Independent reference'
   end subroutine
end program
